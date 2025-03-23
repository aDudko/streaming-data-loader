import asyncio

from aiokafka import AIOKafkaConsumer

from config import KafkaSettings, get_settings
from domain.models import EventModel
from logger import get_logger
from services.event_service import process_events
from utility import Deserializer

logger = get_logger(__name__)


class KafkaConsumerService:

    def __init__(self, settings: KafkaSettings):
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

    async def start(self):
        """ Asynchronous reading of messages from Kafka with a waiting """
        consumer = AIOKafkaConsumer(
            self.settings.consumer_topics,
            bootstrap_servers=self.settings.bootstrap_servers,
            group_id=self.settings.consumer_group,
            key_deserializer=Deserializer.key_deserializer,
            value_deserializer=Deserializer.value_deserializer,
            enable_auto_commit=True
        )
        await consumer.start()
        while True:
            messages = await consumer.getmany(timeout_ms=self.settings.timeout_ms, max_records=self.settings.batch_size)
            events = []
            for topic_partition, messages in messages.items():
                for message in messages:
                    if isinstance(message.value, dict):
                        event = EventModel.event_convert(message.value)
                        events.append(event)
                    else:
                        logger.error(f"Invalid message format: {message.value}")
            if events:
                await process_events(events)


kafka_consumer = KafkaConsumerService(get_settings(KafkaSettings))
