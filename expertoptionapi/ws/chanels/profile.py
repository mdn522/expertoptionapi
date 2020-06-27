"""Module for ExpertOption profile websocket chanel."""
from expertoptionapi.ws.chanels.base import Base


class Profile(Base):
    """Class for Binary profile websocket chanel."""

    action = "profile"

    def __call__(self, ns: str = None, json=False):
        """Method to send message to profile websocket chanel."""

        data = {
            "action": self.action,
            "v": 23,
            "message": None,
        }

        if json:
            return data
        else:
            return self.send_websocket_request(self.action, data, ns=ns)
