import asyncio
from http import HTTPStatus

from elasticsearch import AsyncElasticsearch, helpers

from config import ElasticSettings, get_settings
from logger import get_logger
from metrics import response_time_metric, messages_processed, errors_total

logger = get_logger(__name__)


class ElasticsearchClientService:

    def __init__(self, settings: ElasticSettings):
        self.settings = settings
        self.client = AsyncElasticsearch(hosts=self.settings.url)
        self.index = self.settings.index
        self.retry = self.settings.retry
        logger.info("Elasticsearch client initialized.")

    async def connect(self):
        """ Connection to Elasticsearch. Repeats 10 times every 3 seconds in case of failure """
        for _ in range(10):
            if await self.client.ping():
                logger.info("Elasticsearch is available!")
                return
            logger.info("Waiting for Elasticsearch...")
            await asyncio.sleep(3)
        raise ConnectionError("Could not connect to Elasticsearch")

    @response_time_metric.time
    async def bulk_insert(self, events: list):
        """ Adds a stack of documents to Elasticsearch via Bulk API with retraces """
        if not events:
            return

        attempts = 0
        while attempts < self.retry and events:
            operations = [
                {"_index": self.index, "_source": event}
                for event in events
            ]

            try:
                success, failed_items = await helpers.async_bulk(self.client, operations, raise_on_error=False)
                failed_docs = []

                for i, item in enumerate(failed_items):
                    if "index" in item and item["index"].get("status") not in (HTTPStatus.OK, HTTPStatus.CREATED):
                        messages_processed.inc()
                    else:
                        failed_docs.append(events[i])

                if not failed_docs:
                    logger.info(f"Successfully inserted {len(events)} documents.")
                    return
                else:
                    logger.warning(f"{len(failed_docs)} documents failed. Retrying...")
                    events = failed_docs  # Keep only the failed documents
                    attempts += 1
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Bulk insert failed on attempt {attempts + 1}: {e}")
                await asyncio.sleep(2)

        if events:
            logger.error(f"Could not insert {len(events)} documents after {self.retry} attempts.")
            for doc in events:
                errors_total.inc()
                logger.error(f"Failed document: {doc}")


elasticsearch_client = ElasticsearchClientService(get_settings(ElasticSettings))
