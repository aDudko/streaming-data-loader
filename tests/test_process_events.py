import pytest
from unittest.mock import AsyncMock, MagicMock
from metrics import messages_processed, errors_total
from services.event_service import process_events


@pytest.mark.asyncio
@pytest.mark.parametrize("events, side_effect, expected_bulk_called, expected_processed, expected_errors, expect_log", [
    ([{"field": "value"}], None, True, 1, 0, False),
    ([], None, False, 0, 0, False),
    ([{"field": "value"}], RuntimeError("fail"), True, 0, 1, True),
])
async def test_process_events_behavior(events, side_effect, expected_bulk_called, expected_processed, expected_errors, expect_log, caplog):
    mock_client = MagicMock()
    mock_client.bulk_insert = AsyncMock()

    if side_effect:
        mock_client.bulk_insert.side_effect = side_effect

    messages_processed._value.set(0)
    errors_total._value.set(0)

    with caplog.at_level("ERROR"):
        await process_events(mock_client, events)

    if expected_bulk_called:
        mock_client.bulk_insert.assert_awaited_once()
    else:
        mock_client.bulk_insert.assert_not_called()

    assert messages_processed._value.get() == expected_processed
    assert errors_total._value.get() == expected_errors

    if expect_log:
        assert any("Bulk insert failed" in r.message for r in caplog.records)
