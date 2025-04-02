"""
test_bulk_insert_success: All events inserted successfully
test_bulk_insert_empty_events: No events to insert
test_bulk_insert_partial_fail_then_success: At first attempt some events failed - repeat
test_bulk_insert_exceeds_retries_logs_error: All attempts failed - errors are logged
test_connect_success: Connection to ES is successful
test_connect_failure: Connection to ES is unsuccessful
"""

import pytest
from unittest.mock import AsyncMock, patch

from config import ElasticSettings
from ports.output.elastic_service import ElasticsearchClientService


@pytest.mark.asyncio
async def test_bulk_insert_success():
    service = ElasticsearchClientService(ElasticSettings())
    events = [{"doc": "value"}]

    with patch("ports.output.elastic_service.helpers.async_bulk", new_callable=AsyncMock) as mock_bulk:
        mock_bulk.return_value = (1, [])
        await service.bulk_insert(events)
        mock_bulk.assert_awaited_once()
        args, _ = mock_bulk.await_args
        assert args[1][0]["_source"] == {"doc": "value"}


@pytest.mark.asyncio
async def test_bulk_insert_empty_events():
    service = ElasticsearchClientService(ElasticSettings())
    with patch("ports.output.elastic_service.helpers.async_bulk", new_callable=AsyncMock) as mock_bulk:
        await service.bulk_insert([])
        mock_bulk.assert_not_awaited()


@pytest.mark.asyncio
async def test_bulk_insert_partial_fail_then_success():
    service = ElasticsearchClientService(ElasticSettings())
    events = [{"doc": f"value{i}"} for i in range(2)]

    failed_items = [
        {"index": {"status": 500}},
        {"index": {"status": 201}},  # one succeeds
    ]

    with patch("ports.output.elastic_service.helpers.async_bulk", new_callable=AsyncMock) as mock_bulk:
        # 1st call fails one doc, 2nd succeeds
        mock_bulk.side_effect = [
            (1, failed_items),
            (1, []),
        ]
        await service.bulk_insert(events)
        assert mock_bulk.await_count == 2


@pytest.mark.asyncio
async def test_bulk_insert_exceeds_retries_logs_error(caplog):
    service = ElasticsearchClientService(ElasticSettings(retry=2))
    events = [{"doc": "value"}]

    failed_items = [{"index": {"status": 500}}]

    with patch("ports.output.elastic_service.helpers.async_bulk", new_callable=AsyncMock) as mock_bulk:
        mock_bulk.return_value = (0, failed_items)
        await service.bulk_insert(events)

        assert "Could not insert" in caplog.text
        assert "Failed document" in caplog.text
        assert mock_bulk.await_count == 2


@pytest.mark.asyncio
async def test_connect_success():
    service = ElasticsearchClientService(ElasticSettings())
    with patch.object(service.client, "ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = True
        await service.connect()
        mock_ping.assert_awaited()


@pytest.mark.asyncio
async def test_connect_failure():
    service = ElasticsearchClientService(ElasticSettings())

    with patch.object(service.client, "ping", new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = False
        with pytest.raises(ConnectionError):
            await service.connect()
