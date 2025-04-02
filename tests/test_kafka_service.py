import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiokafka.structs import TopicPartition
from config import KafkaSettings
from ports.input.kafka_service import KafkaConsumerService


@pytest.mark.asyncio
async def test_connect_success():
    mock_consumer = AsyncMock()
    mock_consumer.start = AsyncMock()
    mock_consumer.stop = AsyncMock()

    with patch("ports.input.kafka_service.AIOKafkaConsumer", return_value=mock_consumer):
        service = KafkaConsumerService(elastic_client=MagicMock(), settings=KafkaSettings())
        await service.connect()
        mock_consumer.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_failure():
    with patch("ports.input.kafka_service.AIOKafkaConsumer", side_effect=Exception("Kafka down")):
        service = KafkaConsumerService(elastic_client=MagicMock(), settings=KafkaSettings())
        with pytest.raises(ConnectionError, match="Could not connect to Kafka"):
            await service.connect()


@pytest.mark.asyncio
async def test_start_consumes_valid_messages_and_commits():
    consumer_mock = AsyncMock()
    tp = TopicPartition("topic_name", 0)
    message_mock = MagicMock()
    message_mock.value = {"field": "value"}
    message_mock.offset = 10

    consumer_mock.start = AsyncMock()
    consumer_mock.stop = AsyncMock()
    consumer_mock.commit = AsyncMock()
    consumer_mock.getmany.side_effect = [
        {tp: [message_mock]},
        asyncio.CancelledError()
    ]

    with patch("ports.input.kafka_service.AIOKafkaConsumer", return_value=consumer_mock):
        with patch("ports.input.kafka_service.process_events", new_callable=AsyncMock) as process_events_mock:
            service = KafkaConsumerService(elastic_client=MagicMock(), settings=KafkaSettings())
            try:
                await service.start()
            except asyncio.CancelledError:
                pass

            process_events_mock.assert_called_once()
            consumer_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_start_handles_invalid_message_format():
    consumer_mock = AsyncMock()
    tp = TopicPartition("topic_name", 0)
    message_mock = MagicMock()
    message_mock.value = "invalid"  # не dict
    message_mock.offset = 5

    consumer_mock.start = AsyncMock()
    consumer_mock.stop = AsyncMock()
    consumer_mock.commit = AsyncMock()
    consumer_mock.getmany = AsyncMock(side_effect=asyncio.CancelledError())

    with patch("ports.input.kafka_service.AIOKafkaConsumer", return_value=consumer_mock):
        with patch("ports.input.kafka_service.process_events", new_callable=AsyncMock) as process_events_mock:
            service = KafkaConsumerService(elastic_client=MagicMock(), settings=KafkaSettings())
            try:
                await service.start()
            except asyncio.CancelledError:
                pass

            process_events_mock.assert_not_called()
            consumer_mock.commit.assert_not_called()


@pytest.mark.asyncio
async def test_start_does_not_commit_if_process_events_fails():
    consumer_mock = AsyncMock()
    tp = TopicPartition("topic_name", 0)
    message_mock = MagicMock()
    message_mock.value = {"field": "value"}
    message_mock.offset = 10

    consumer_mock.start = AsyncMock()
    consumer_mock.stop = AsyncMock()
    consumer_mock.commit = AsyncMock()
    consumer_mock.getmany = AsyncMock(return_value={tp: [message_mock]})

    with patch("ports.input.kafka_service.AIOKafkaConsumer", return_value=consumer_mock):
        with patch("ports.input.kafka_service.process_events", new_callable=AsyncMock) as process_events_mock:
            process_events_mock.side_effect = Exception("fail")
            service = KafkaConsumerService(elastic_client=MagicMock(), settings=KafkaSettings())

            with pytest.raises(Exception, match="fail"):
                await service.start()

            consumer_mock.commit.assert_not_called()
