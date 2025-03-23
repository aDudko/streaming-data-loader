import time

from metrics import transform_time_metric


class EventModel:

    @staticmethod
    @transform_time_metric.time
    def event_convert(event: dict) -> dict:
        """ Data transformation """
        event["timestamp"] = int(time.time())
        return event
