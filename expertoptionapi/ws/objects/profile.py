"""Module for ExpertOption Profile websocket object."""
from expertoptionapi.ws.objects.base import Base


class Profile(Base):
    """Class for ExpertOption Profile websocket object."""

    def __init__(self):
        super().__init__()
        self.__name = "profile"
        self.__balance = None
        self.__msg = None

    # ----------------------------------------------------------------
    @property
    def balance(self):
        """Property to get balance value.

        :returns: The balance value.
        """
        return self.__balance

    @balance.setter
    def balance(self, balance):
        """Method to set balance value."""
        self.__balance = balance

    # ---------------------------------------------------------------------
    @property
    def user_id(self):
        """Property to get user id value.

        :returns: The user id value.
        """
        return self.msg.get('id')

    # ------------------------------------------------------------------------
    @property
    def is_demo(self):
        return 'demo_balance' in self.msg and self.msg['is_demo'] == 1

    # ------------------------------------------------------------------------
    @property
    def is_real(self):
        return 'real_balance' in self.msg and self.msg['is_demo'] == 0

    # ------------
    @property
    def msg(self):
        return self.__msg

    @msg.setter
    def msg(self, msg):
        self.__msg = msg
