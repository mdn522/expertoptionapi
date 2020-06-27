"""Module for ExpertOption multipleAction websocket chanel."""
from expertoptionapi.ws.chanels.base import Base


class MultipleAction(Base):
    """Class for Binary multipleAction websocket chanel."""

    action = "multipleAction"

    def __call__(self, actions: list, ns: str = None, json=False):
        """Method to send message to multipleAction websocket chanel."""

        data = {
            "action": self.action,
            "v": 23,
            "message": {
                "token": self.api.token,
                "actions": actions,
            },
        }

        if json:
            return data
        else:
            return self.send_websocket_request(self.action, data, ns=ns)
