from logger import get_logger
from metrics import batch_processing_time_metric, messages_processed, errors_total
from ports.output.elastic_service import ElasticsearchClientService

logger = get_logger(__name__)


@batch_processing_time_metric.time()
async def process_events(elastic_client: ElasticsearchClientService, events: list[dict]) -> None:
    if not events:
        return
    try:
        await elastic_client.bulk_insert(events)
    except Exception as e:
        logger.exception("Bulk insert failed")
        errors_total.inc()
    else:
        messages_processed.inc(len(events))
