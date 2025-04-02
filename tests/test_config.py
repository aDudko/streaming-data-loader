"""
test_default_settings: Check for default values
test_env_override: Override via environment variables
test_invalid_env_values: Error on wrong variable type
test_settings_are_cached: Caching of settings
test_env_file_override: Read values from .env
"""

import pytest
from pydantic import ValidationError

from config import get_settings, KafkaSettings, ElasticSettings, PrometheusSettings

# --- Fixtures ----------------------------------------------------------------

@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    """ Disables dotenv everywhere (automatically) """
    monkeypatch.setattr("config.dotenv.load_dotenv", lambda *a, **kw: None)


@pytest.fixture
def clean_env(monkeypatch):
    """ Deletes environment variables and resets the cache """

    def _clean(vars_to_delete: list[str]):
        for var in vars_to_delete:
            monkeypatch.delenv(var, raising=False)
        get_settings.cache_clear()

    return _clean


# --- Default values ----------------------------------------------------------

@pytest.mark.parametrize("settings_class, expected_values, env_vars", [
    (
            KafkaSettings,
            {
                "bootstrap_servers": "kafka-cluster:9092",
                "consumer_topics": "topic_name",
                "consumer_group": "consumer_group_name",
                "batch_size": 100,
                "timeout_ms": 5000,
            },
            [
                "KAFKA_BOOTSTRAP_SERVERS",
                "KAFKA_CONSUMER_TOPICS",
                "KAFKA_CONSUMER_GROUP",
                "KAFKA_BATCH_SIZE",
                "KAFKA_TIMEOUT_MS",
            ]
    ),
    (
            ElasticSettings,
            {
                "url": "http://elasticsearch:9200",
                "index": "index_name",
                "retry": 3,
            },
            [
                "ELASTIC_URL",
                "ELASTIC_INDEX",
                "ELASTIC_RETRY",
            ]
    ),
    (
            PrometheusSettings,
            {
                "port": 9090,
            },
            ["PROMETHEUS_PORT"]
    ),
])
def test_default_settings(settings_class, expected_values, env_vars, clean_env):
    clean_env(env_vars)
    settings = get_settings(settings_class)

    for key, expected in expected_values.items():
        actual = getattr(settings, key)
        assert actual == expected, f"{key}: expected {expected}, got {actual}"


# --- Override via os.environ --------------------------------------------------

@pytest.mark.parametrize("env_var, value, settings_class, attr, expected", [
    ("KAFKA_BATCH_SIZE", "200", KafkaSettings, "batch_size", 200),
    ("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092", KafkaSettings, "bootstrap_servers", "kafka1:9092"),
    ("ELASTIC_INDEX", "custom_index", ElasticSettings, "index", "custom_index"),
    ("PROMETHEUS_PORT", "8888", PrometheusSettings, "port", 8888),
])
def test_env_override(monkeypatch, env_var, value, settings_class, attr, expected):
    monkeypatch.setenv(env_var, value)
    get_settings.cache_clear()
    settings = get_settings(settings_class)
    assert getattr(settings, attr) == expected


# --- Invalid input should raise ValidationError -------------------------------

@pytest.mark.parametrize("env_var, value, settings_class", [
    ("KAFKA_BATCH_SIZE", "not_a_number", KafkaSettings),
    ("PROMETHEUS_PORT", "invalid", PrometheusSettings),
])
def test_invalid_env_values(monkeypatch, env_var, value, settings_class):
    monkeypatch.setenv(env_var, value)
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings(settings_class)


# --- Settings should be cached ------------------------------------------------

def test_settings_are_cached(monkeypatch):
    monkeypatch.setenv("KAFKA_TIMEOUT_MS", "1234")
    get_settings.cache_clear()

    s1 = get_settings(KafkaSettings)
    s2 = get_settings(KafkaSettings)
    assert s1 is s2
