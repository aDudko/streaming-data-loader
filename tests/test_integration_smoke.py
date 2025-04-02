import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiokafka.structs import TopicPartition
from ports.input.kafka_service import KafkaConsumerService
from config import KafkaSettings


@pytest.mark.asyncio
@pytest.mark.parametrize("events_by_tp, should_process, raises_error, expected_processed, expected_errors", [
    (
            {TopicPartition("test-topic", 0): [{"field": "value1"}, {"field": "value2"}]},
            True, False, 2, 0
    ),
    (
            {TopicPartition("test-topic", 0): ["invalid"]},
            False, False, 0, 0
    ),
    (
            {},  # empty batch
            False, False, 0, 0
    ),
    (
            {TopicPartition("test-topic", 0): [{"field": "fail"}]},
            True, True, 0, 1
    ),
    (
            {
                TopicPartition("topic-1", 0): [{"field": "v1"}],
                TopicPartition("topic-2", 1): [{"field": "v2"}, {"field": "v3"}],
            },
            True, False, 3, 0
    )
])
async def test_kafka_to_elastic_smoke_flow(events_by_tp, should_process, raises_error, expected_processed,
                                           expected_errors):
    consumer_mock = AsyncMock()
    consumer_mock.start = AsyncMock()
    consumer_mock.stop = AsyncMock()
    consumer_mock.commit = AsyncMock()

    # Preparation of messages
    events = []
    for tp, msgs in events_by_tp.items():
        msg_list = []
        for i, val in enumerate(msgs):
            m = MagicMock()
            m.offset = 100 + i
            m.value = val
            msg_list.append(m)
        events_by_tp[tp] = msg_list
        events.extend(val for val in msgs if isinstance(val, dict))

    consumer_mock.getmany = AsyncMock(return_value=events_by_tp)

    with patch("ports.input.kafka_service.AIOKafkaConsumer", return_value=consumer_mock):
        with patch("ports.input.kafka_service.process_events", new_callable=AsyncMock) as process_events_mock:
            if raises_error:
                process_events_mock.side_effect = Exception("Simulated failure")

            service = KafkaConsumerService(
                elastic_client=MagicMock(),
                settings=KafkaSettings()
            )

            # Abort after the first iteration
            consumer_mock.getmany.side_effect = [
                events_by_tp,
                asyncio.CancelledError()
            ]

            if raises_error:
                with pytest.raises(Exception, match="Simulated failure"):
                    await service.start()
            else:
                try:
                    await service.start()
                except asyncio.CancelledError:
                    pass

            if should_process:
                process_events_mock.assert_called_once()
            else:
                process_events_mock.assert_not_called()

            if raises_error:
                consumer_mock.commit.assert_not_called()
            elif should_process:
                consumer_mock.commit.assert_called_once()
