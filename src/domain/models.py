import time


class EventModel:

    def __init__(self, event: dict):
        self.event = event

    def event_convert(self) -> dict:
        return self.__convert()

    def __convert(self) -> dict:
        """ Data transformation """
        self.event["timestamp"] = int(time.time())
        return self.event
