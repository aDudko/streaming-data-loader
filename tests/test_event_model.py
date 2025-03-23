import time

import pytest

from domain.models import EventModel

@pytest.mark.asyncio(scope="function")
def test_event_convert():
    event = {"key": "value"}
    converted_event = EventModel.event_convert(event)

    assert "timestamp" in converted_event, "The 'timestamp' field must be present"
    assert isinstance(converted_event["timestamp"], int), "The 'timestamp' field must be a whole number"
    assert abs(converted_event["timestamp"] - int(time.time())) < 2, "Incorrect timestamp value"

    # Checking that other fields have not changed
    assert converted_event["key"] == "value", "The 'key' field must remain unchanged"

@pytest.mark.asyncio(scope="function")
def test_event_convert_empty():
    event = {}
    converted_event = EventModel.event_convert(event)

    assert "timestamp" in converted_event, "The 'timestamp' field must be present in an empty event"
    assert isinstance(converted_event["timestamp"], int), "The 'timestamp' field must be a whole number"

@pytest.mark.asyncio(scope="function")
def test_event_convert_overwrite_timestamp():
    old_timestamp = 1234567890
    event = {"timestamp": old_timestamp}
    converted_event = EventModel.event_convert(event)

    assert converted_event["timestamp"] != old_timestamp, "The old timestamp must be overwritten"
    assert abs(converted_event["timestamp"] - int(time.time())) < 2, "Incorrect timestamp value"
