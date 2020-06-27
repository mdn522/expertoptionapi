"""Module for ExpertOption unsubscribe websocket chanel."""
from expertoptionapi.ws.chanels.base import Base


class Unsubscribe(Base):
    """Class for Binary unsubscribe websocket chanel."""

    action = "unsubscribe"

    def __call__(self, assetid, ns: str = None, json=False):
        """Method to send message to unsubscribe websocket chanel.
        """

        if isinstance(assetid, int):
            assetid = [assetid]
        # TODO Support asset name

        data = {
            "action": self.action,
            "v": 23,
            "message": {
                "assetid": assetid,
            },
        }

        if json:
            return data
        else:
            return self.send_websocket_request(self.action, data, ns=ns or "_synth._common.unsubscribe-" + self.api.request_id)
