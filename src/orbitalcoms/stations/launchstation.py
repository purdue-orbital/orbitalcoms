from typing import Any

from ..coms import ComsMessage
from .station import Station


class LaunchStation(Station):
    def _on_send(self, new: ComsMessage) -> Any:
        if new.DATA is not None:
            self._last_data = new.DATA

    @property
    def abort(self) -> bool:
        if self.last_recieved is None:
            return False
        return bool(self.last_recieved.ABORT)

    @property
    def qdm(self) -> bool:
        if self.last_recieved is None:
            return False
        return bool(self.last_recieved.QDM)

    @property
    def stab(self) -> bool:
        if self.last_recieved is None:
            return False
        return bool(self.last_recieved.STAB)

    @property
    def launch(self) -> bool:
        if self.last_recieved is None:
            return False
        return bool(self.last_recieved.LAUNCH)

    @property
    def armed(self) -> bool:
        if self.last_recieved is None:
            return False
        return bool(self.last_recieved.ARMED)
