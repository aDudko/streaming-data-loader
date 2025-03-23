from functools import lru_cache
from typing import Type, TypeVar

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

TSettings = TypeVar("TSettings", bound=BaseSettings)


@lru_cache
def get_settings(cls: Type[TSettings]) -> TSettings:
    dotenv.load_dotenv()
    return cls()


class ApplicationSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True)

    pod_name: str = "streaming-data-loader"
    replicas: int = 0


application_settings: ApplicationSettings = get_settings(ApplicationSettings)


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="kafka_")

    bootstrap_servers: str = "kafka-cluster:9092"
    consumer_topics: str = "topic_name"
    consumer_group: str = "consumer_group_name"
    batch_size: int = 100
    timeout_ms: int = 5000


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(
        str_strip_whitespace=True, env_prefix="elastic_"
    )

    url: str = "http://elasticsearch:9200"
    index: str = "index_name"
    retry: int = 3
