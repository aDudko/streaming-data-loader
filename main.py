import asyncio

import metrics
from config import KafkaSettings, ElasticSettings, get_settings
from logger import get_logger
from ports.input.kafka_service import KafkaConsumerService
from ports.output.elastic_service import ElasticsearchClientService

logger = get_logger(__name__)
kafka_settings: KafkaSettings = get_settings(KafkaSettings)
elastic_settings: ElasticSettings = get_settings(ElasticSettings)

async def main():
    elastic_client = ElasticsearchClientService(settings=elastic_settings)
    kafka_consumer = KafkaConsumerService(elastic_client=elastic_client, settings=kafka_settings)
    await kafka_consumer.connect()
    await elastic_client.connect()
    await kafka_consumer.start()


if __name__ == "__main__":
    try:
        metrics.start_metrics_server()
        asyncio.run(main())
    except Exception as e:
        logger.error(f"StreamingDataLoader error messages: {e}")
