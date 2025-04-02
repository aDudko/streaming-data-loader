import asyncio
import json

from aiokafka import AIOKafkaConsumer, OffsetAndMetadata

from config import KafkaSettings
from domain.models import EventModel
from logger import get_logger
from metrics import consume_time_metric, errors_total
from ports.output.elastic_service import ElasticsearchClientService
from services.event_service import process_events

logger = get_logger(__name__)


class KafkaConsumerService:

    def __init__(self, elastic_client: ElasticsearchClientService, settings: KafkaSettings):
        self.es_client = elastic_client
        self.settings = settings
        logger.info("Kafka Consumer initialized.")

    async def connect(self):
        """ Connection to Kafka. Repeats 10 times every 3 seconds in case of failure """
        for _ in range(10):
            try:
                consumer = AIOKafkaConsumer(
                    self.settings.consumer_topics,
                    bootstrap_servers=self.settings.bootstrap_servers
                )
                await consumer.start()
                await consumer.stop()
                logger.info("Kafka is available!")
                return
            except Exception as e:
                logger.warning(f"Waiting for Kafka... {e}")
                await asyncio.sleep(3)
        raise ConnectionError("Could not connect to Kafka")

    @consume_time_metric.time()
    async def start(self):
        """ Asynchronous reading of messages from Kafka with a waiting """
        consumer = AIOKafkaConsumer(
            self.settings.consumer_topics,
            bootstrap_servers=self.settings.bootstrap_servers,
            group_id=self.settings.consumer_group,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False
        )
        await consumer.start()
        try:
            while True:
                last_offsets = {}
                events = []
                messages = await consumer.getmany(
                    timeout_ms=self.settings.timeout_ms,
                    max_records=self.settings.batch_size)
                for topic_partition, messages in messages.items():
                    for message in messages:
                        if isinstance(message.value, dict):
                            event = EventModel(message.value)
                            events.append(event.event_convert())
                            last_offsets[topic_partition] = message.offset + 1
                        else:
                            errors_total.inc()
                            logger.error(f"Invalid message format: {message.value}")
                if events:
                    await process_events(self.es_client, events)
                    offsets = {
                        topic_partition: OffsetAndMetadata(offset, "")
                        for topic_partition, offset in last_offsets.items()
                    }
                    await consumer.commit(offsets)
        finally:
            await consumer.stop()
