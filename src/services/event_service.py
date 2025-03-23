from typing import List

from ports.output.elastic_service import elasticsearch_client


async def process_events(events: List[dict]):
    await elasticsearch_client.bulk_insert(events)
