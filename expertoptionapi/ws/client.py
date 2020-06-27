"""Module for ExpertOption websocket."""

import simplejson as json
import logging

import websocket
import expertoptionapi.global_value as global_value


class WebsocketClient:
    def __init__(self, api):
        """
        :param api: The instance of :class:`ExpertOptionAPI
            <expertoption.api.ExpertOptionAPI>`.
        """
        self.api = api
        self.wss = websocket.WebSocketApp(
            self.api.wss_url, on_message=self.on_message,
            on_error=self.on_error, on_close=self.on_close,
            on_open=self.on_open,
            # header=self.api.headers, cookie=self.api.cookie  # TODO test are they needed or not
        )

    def on_message(self, message):
        """Method to process websocket messages."""
        logger = logging.getLogger(__name__)
        message = message.decode('utf-8')
        logger.debug(message)

        message = json.loads(message)

        self.handle_action(message)

        if self.api.message_callback is not None:
            try:
                self.api.message_callback(message)
            except:
                pass

    def handle_action(self, message):
        action = message.get('action')
        ns = message.get('ns')

        if ns and ns not in [""]:
            self.api.msg_by_ns[ns] = message
            self.api.msg_by_action[action][ns] = message

        if action == "multipleAction":
            for sub_message in message['message']['actions']:
                self.handle_action(sub_message)
        elif action == 'profile':
            self.api.profile.msg = message['message']['profile']

            try:
                if self.api.profile.is_demo:
                    self.api.profile.balance = message['message']['profile']['demo_balance']
                else:
                    self.api.profile.balance = message['message']['profile']['real_balance']
            except Exception as e:
                print("ERROR" * 16)
                import traceback
                traceback.print_exc()

    @staticmethod
    def on_error(wss, error):  # pylint: disable=unused-argument
        """Method to process websocket errors."""
        logger = logging.getLogger(__name__)
        logger.error(error)
        global_value.check_websocket_if_connect = -1

    @staticmethod
    def on_open(wss):  # pylint: disable=unused-argument
        """Method to process websocket open."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket client connected.")
        global_value.check_websocket_if_connect = 1

    @staticmethod
    def on_close(wss):  # pylint: disable=unused-argument
        """Method to process websocket close."""
        logger = logging.getLogger(__name__)
        logger.debug("Websocket connection closed.")
        global_value.check_websocket_if_connect = 0
