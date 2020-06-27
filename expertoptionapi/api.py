"""Module for Expert Option API."""
import decimal
import ssl
import time
import logging
import urllib

import pause
import threading
import simplejson as json
from threading import Thread
from collections import defaultdict, OrderedDict

import websocket

from expertoptionapi.constants import REGION
from expertoptionapi.ws.chanels.multiple_action import MultipleAction
from expertoptionapi.ws.chanels.ping import Ping
from expertoptionapi.ws.objects.profile import Profile
from expertoptionapi.ws.client import WebsocketClient
import expertoptionapi.global_value as global_value


# noinspection PyShadowingBuiltins
def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


class FixSizeOrderedDict(OrderedDict):
    # noinspection PyShadowingBuiltins
    def __init__(self, *args, max=0, **kwargs):
        self._max = max
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        if self._max > 0:
            if len(self) > self._max:
                self.popitem(False)


class ExpertOptionAPI:
    websocket_thread: Thread
    ping_thread: Thread  # TODO support it
    profile = Profile()
    message_callback = None

    results = FixSizeOrderedDict(max=300)
    msg_by_ns = FixSizeOrderedDict(max=300)
    msg_by_action = nested_dict(1, lambda: FixSizeOrderedDict(max=300))
    _request_id = 1

    def __init__(self, token, server_region=REGION.EUROPE, ):
        self.token = token

        self.wss_url = server_region

        self.websocket_client = None

    def connect(self):
        global_value.check_websocket_if_connect = None

        self.websocket_client = WebsocketClient(self)

        self.websocket_thread = threading.Thread(target=self.websocket.run_forever, kwargs={
            'sslopt': {
                "check_hostname": False,
                "cert_reqs": ssl.CERT_NONE,
                "ca_certs": "cacert.pem"
            },
            "ping_interval": 0,
            'skip_utf8_validation': True,
            "origin": "https://app.expertoption.com",
            # "http_proxy_host": '127.0.0.1', "http_proxy_port": 8890
        })

        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        while True:
            try:
                if global_value.check_websocket_if_connect == 0 or global_value.check_websocket_if_connect == -1:
                    return False
                elif global_value.check_websocket_if_connect == 1:
                    break
            except Exception:
                pass
            pass

        # self.authorize(authorize=self.token)

        # TODO support it
        # self.multiple_action(actions=[
        #     self.get_countries(json=True),
        #     self.get_currency(json=True),
        #     self.get_profile(json=True),
        #     self.get_environment(json=True),
        #     self.get_open_options(json=True),
        #     self.get_user_group(json=True),
        #     self.get_set_time_zone(json=True),
        #     self.get_history_steps(json=True),
        #     self.get_trade_history(json=True),
        # ], ns="_common")

        self.send_websocket_request(action="multipleAction",
                                    msg={"token": self.token, "v": 18, "action": "multipleAction",
                                         "message": {"token": self.token, "actions": [
                                             {"action": "getCountries", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "getCurrency", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "profile", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "environment", "message": None, "ns": None, "v": 18,
                                              "token": self.token}, {"action": "assets",
                                                                     "message": {"mode": ["vanilla", "binary"],
                                                                                 "subscribeMode": ["vanilla"]},
                                                                     "ns": None, "v": 18, "token": self.token},
                                             {"action": "openOptions", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "userGroup", "message": None, "ns": None, "v": 18,
                                              "token": self.token},
                                             {"action": "setTimeZone", "message": {"timeZone": 360}, "ns": None,
                                              "v": 18, "token": self.token},
                                             {"action": "historySteps", "message": None, "ns": None, "v": 18,
                                              "token": self.token}, {"action": "tradeHistory",
                                                                     "message": {"mode": ["binary", "vanilla"],
                                                                                 "count": 100, "index_from": 0},
                                                                     "ns": None, "v": 18, "token": self.token}]}},
                                    ns="_common")

        self.ping_thread = threading.Thread(target=self.auto_ping)
        self.ping_thread.daemon = True
        self.ping_thread.start()

        start_t = time.time()
        while self.profile.msg is None:
            if time.time() - start_t >= 30:
                logging.error('**error** profile late 30 sec')
                return False

            pause.seconds(0.01)

        return True

    def auto_ping(self):
        while True:
            try:
                self.ping()
                pause.seconds(5)
            except:
                pass

    @property
    def multiple_action(self):
        return MultipleAction(self).__call__

    @property
    def ping(self):
        return Ping(self).__call__

    @property
    def websocket(self):
        """Property to get websocket.
        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    # def authorize(self):
    #     self.websocket.send(json.dumps({"authorize": self.token}))

    def close(self):
        self.websocket.close()
        self.websocket_thread.join()

    def websocket_alive(self):
        return self.websocket_thread.is_alive()

    @property
    def request_id(self):
        self._request_id += 1
        return str(self._request_id - 1)

    def send_websocket_request(self, action: str, msg, ns: str = None):
        """Send websocket request to ExpertOption server.
        :type action: str
        :param ns: str
        :param dict msg: The websocket request msg.
        """
        logger = logging.getLogger(__name__)

        if ns is not None and not ns:
            ns = self.request_id

        msg['ns'] = ns

        if ns:
            # self.results[ns] = None
            self.msg_by_ns[ns] = None
            self.msg_by_action[action][ns] = None

        def default(obj):
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            raise TypeError

        data = json.dumps(msg, default=default)
        logger.debug(data)

        self.websocket.send(bytearray(urllib.parse.quote(data).encode('utf-8')), opcode=websocket.ABNF.OPCODE_BINARY)
        return ns
