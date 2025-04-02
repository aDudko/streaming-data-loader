from prometheus_client import Counter, Summary, CollectorRegistry, start_http_server
from typing import Callable, Optional, Coroutine, Any
import functools
import time

from logger import get_logger

logger = get_logger(__name__)

registry = CollectorRegistry()

# Counters
messages_processed = Counter("messages_processed_total", "Total number of processed messages")
errors_total = Counter("errors_total", "Total number of errors")

# Runtime metrics
consume_time_metric = Summary("consume_duration_seconds", "Time spent consuming messages")
response_time_metric = Summary("response_duration_seconds", "Time spent to response")
transform_time_metric = Summary("transform_duration_seconds", "Time spent transforming messages")
batch_processing_time_metric = Summary("batch_processing_duration_seconds", "Time spent processing the entire batch")


def start_metrics_server(port: int = 8000):
    logger.info(f"Starting Prometheus metrics server on port {port}")
    start_http_server(port)


def counter_metric_decorator(
        metric: Optional[Summary] = None,
        catch_exception: bool = True
) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Coroutine[Any, Any, Any]]]:
    """ Decorator for counting processed messages, errors and execution time """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                errors_total.inc()
                if catch_exception:
                    raise e
                logger.error(f"Error in {func.__name__}: {e}")
                raise e
            finally:
                if metric:
                    duration = time.time() - start_time
                    metric.observe(duration)

        return async_wrapper

    return decorator
