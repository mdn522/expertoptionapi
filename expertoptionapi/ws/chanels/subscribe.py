"""Module for ExpertOption subscribe websocket chanel."""
from expertoptionapi.ws.chanels.base import Base


class Subscribe(Base):
    """Class for Binary subscribe websocket chanel."""

    action = "subscribe"

    def __call__(self, mode: str, assetid, ns: str = None, json=False):
        """Method to send message to subscribe websocket chanel.
        :type mode: string - vanilla or binary
        """

        if isinstance(assetid, int):
            assetid = [assetid]
        # TODO Support asset name

        data = {
            "action": self.action,
            "v": 23,
            "message": {
                "mode": mode,
                "assetid": assetid,
            },
        }

        if json:
            return data
        else:
            return self.send_websocket_request(self.action, data, ns=ns or "_synth._common.subscribe-" + self.api.request_id)
