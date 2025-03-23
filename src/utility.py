import json


class Deserializer:

    @staticmethod
    def key_deserializer(key):
        return key.decode('utf-8')

    @staticmethod
    def value_deserializer(value):
        return json.loads(value.decode('utf-8'))
