from typing import List

from metrics import batch_processing_time_metric, messages_processed
from ports.output.elastic_service import elasticsearch_client


@batch_processing_time_metric.time
async def process_events(events: List[dict]):
    await elasticsearch_client.bulk_insert(events)
    messages_processed.inc(len(events))
