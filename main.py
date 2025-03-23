import asyncio

from logger import get_logger
from ports.input.kafka_service import kafka_consumer
from ports.output.elastic_service import elasticsearch_client

logger = get_logger(__name__)


async def main():
    await kafka_consumer.connect()
    await elasticsearch_client.connect()
    await kafka_consumer.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"StreamingDataLoader error messages: {e}")
