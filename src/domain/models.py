import time


class EventModel:

    @staticmethod
    def event_convert(event: dict) -> dict:
        """ Data transformation """
        event["timestamp"] = int(time.time())
        return event
