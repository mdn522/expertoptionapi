from expertoptionapi import global_value
from expertoptionapi.api import ExpertOptionAPI
import expertoptionapi.constants as OP_code
import time
import logging

from collections import defaultdict


# noinspection PyShadowingBuiltins
def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


class ExpertOption:
    api: ExpertOptionAPI

    def __init__(self, token, server_region=OP_code.REGION.EUROPE, message_callback=None, on_open=None):
        self.token = token
        self.server_region = server_region

        self.message_callback = message_callback
        self.on_open = on_open

        self.max_reconnect = 5
        self.connect_count = 0
        self.suspend = 0.5

        self.connect()

    def connect(self):
        while True:
            try:
                self.api.close()
            except Exception:
                pass
                # logging.error('**warning** self.api.close() fail')
            if self.connect_count < self.max_reconnect or self.max_reconnect < 0:
                self.api = ExpertOptionAPI(self.token, self.server_region)
                self.api.message_callback = self.message_callback
                self.api.on_open = self.on_open
                check = None

                check = self.api.connect()

                if check:
                    break

                time.sleep(self.suspend * 2)
                self.connect_count = self.connect_count + 1
            else:
                logging.error(
                    '**error** reconnect() too many time please look log file')

    @staticmethod
    def check_connect():
        # True/False
        return global_value.check_websocket_if_connect == 1
