from prometheus_client import Counter, Summary, push_to_gateway, CollectorRegistry, start_http_server
import functools
import time

from config import PushgatewaySettings, get_settings
from logger import get_logger

logger = get_logger(__name__)

settings = get_settings(PushgatewaySettings)
registry = CollectorRegistry()

# Counters
messages_processed = Counter("messages_processed_total", "Total number of processed messages")
errors_total = Counter("errors_total", "Total number of errors")

# Runtime metrics
consume_time_metric = Summary("consume_duration_seconds", "Time spent consuming messages")
response_time_metric = Summary("response_duration_seconds", "Time spent to response")
transform_time_metric = Summary("transform_duration_seconds", "Time spent transforming messages")
batch_processing_time_metric = Summary("batch_processing_duration_seconds", "Time spent processing the entire batch")


def counter_metric_decorator(metric: Summary = None, catch_exception: bool = True):
    """ Decorator for counting processed messages, errors and execution time """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                messages_processed.inc()
                return result
            except Exception as e:
                errors_total.inc()
                if catch_exception:
                    raise e
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                raise e
            finally:
                if metric:
                    duration = time.time() - start_time
                    metric.observe(duration)

        return wrapper

    return decorator


push_to_gateway(settings.url, job='streaming-data-loader', registry=registry)
start_http_server(8000)
