from typing import Any

from ..coms import ComsMessage
from .station import Station


class LaunchStation(Station):
    def _on_send(self, new: ComsMessage) -> Any:
        if new.DATA is not None:
            self._last_data = new.DATA

    @property
    def abort(self) -> bool:
        if self.last_received is None:
            return False
        return bool(self.last_received.ABORT)

    @property
    def qdm(self) -> bool:
        if self.last_received is None:
            return False
        return bool(self.last_received.QDM)

    @property
    def stab(self) -> bool:
        if self.last_received is None:
            return False
        return bool(self.last_received.STAB)

    @property
    def launch(self) -> bool:
        if self.last_received is None:
            return False
        return bool(self.last_received.LAUNCH)

    @property
    def armed(self) -> bool:
        if self.last_received is None:
            return False
        return bool(self.last_received.ARMED)
