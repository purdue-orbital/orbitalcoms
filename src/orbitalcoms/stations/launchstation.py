from typing import Any

from ..coms import ComsMessage
from .station import Station


class LaunchStation(Station):
    def _on_send(self, new: ComsMessage) -> Any:
        """Set data to most accurate version

        ``LaunchStation`` does have access to read mission data from
        the source it assumes that data being sent is the most accurate
        and sets ``_last_data`` property appropriately

        :param new: Newly recieved message
        :type new: ComsMessage
        :returns: Nothing of importance
        :rtype: Any
        """
        if new.DATA is not None:
            self._last_data = new.DATA

    @property
    def abort(self) -> bool:
        """Current station abort property

        :returns: The boolean value of the station abort status
        :rtype: bool
        """
        if self.last_received is None:
            return False
        return bool(self.last_received.ABORT)

    @property
    def qdm(self) -> bool:
        """Current station QDM property

        :returns: The boolean value of the station QDM status
        :rtype: bool
        """
        if self.last_received is None:
            return False
        return bool(self.last_received.QDM)

    @property
    def stab(self) -> bool:
        """Current station stabilize property

        :returns: The boolean value of the station stabilize status
        :rtype: bool
        """
        if self.last_received is None:
            return False
        return bool(self.last_received.STAB)

    @property
    def launch(self) -> bool:
        """Current station launch property

        :returns: The boolean value of the station launch status
        :rtype: bool
        """
        if self.last_received is None:
            return False
        return bool(self.last_received.LAUNCH)

    @property
    def armed(self) -> bool:
        """Current station armed property

        :returns: The boolean value of the station armed status
        :rtype: bool
        """
        if self.last_received is None:
            return False
        return bool(self.last_received.ARMED)
