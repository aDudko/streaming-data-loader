"""
test_event_model_adds_timestamp: timestamp present
test_event_model_overwrites_existing_timestamp: timestamp is overwritten
test_event_model_preserves_other_fields: other fields are preserved
test_event_model_does_not_mutate_original: original dict is not mutated
test_event_model_handles_empty_dict: empty dict handled
test_event_model_overwrites_none_timestamp: None timestamp is overwritten
test_event_model_preserves_nested_structure: nested structure preserved
test_event_model_modifies_in_place: in-place modification
"""

from domain.models import EventModel
import time


def test_event_model_adds_timestamp():
    model = EventModel({"field": "value"})
    result = model.event_convert()

    assert "timestamp" in result
    assert isinstance(result["timestamp"], int)
    assert abs(result["timestamp"] - int(time.time())) < 5  # within reasonable delta


def test_event_model_overwrites_existing_timestamp():
    original = {"field": "value", "timestamp": 1234567890}
    model = EventModel(original)
    converted = model.event_convert()

    assert converted["timestamp"] != 1234567890
    assert abs(converted["timestamp"] - int(time.time())) < 5


def test_event_model_preserves_other_fields():
    original = {"foo": "bar", "baz": 42}
    model = EventModel(original)
    converted = model.event_convert()

    assert converted["foo"] == "bar"
    assert converted["baz"] == 42
    assert "timestamp" in converted


def test_event_model_does_not_mutate_original():
    original = {"field": "value"}
    model = EventModel(original)
    converted = model.event_convert()

    assert "timestamp" in original
    assert converted is original


def test_event_model_handles_empty_dict():
    model = EventModel({})
    result = model.event_convert()
    assert "timestamp" in result
    assert len(result) == 1


def test_event_model_overwrites_none_timestamp():
    original = {"timestamp": None}
    model = EventModel(original)
    result = model.event_convert()

    assert isinstance(result["timestamp"], int)
    assert result["timestamp"] is not None


def test_event_model_preserves_nested_structure():
    original = {
        "level1": {
            "list": [1, 2, {"deep": "value"}],
            "inner": {"key": "val"}
        }
    }
    model = EventModel(original)
    result = model.event_convert()

    assert result["level1"]["list"][2]["deep"] == "value"
    assert result["level1"]["inner"]["key"] == "val"


def test_event_model_modifies_in_place():
    original = {"a": 1}
    model = EventModel(original)
    result = model.event_convert()

    assert result is original
