from typing import Any

from ..coms import ComsMessage
from .station import Station


class GroundStation(Station):
    def _on_receive(self, new: ComsMessage) -> Any:
        if new.DATA is not None:
            self._last_data = new.DATA

    @property
    def abort(self) -> bool:
        if self.last_sent is None:
            return False
        return bool(self.last_sent.ABORT)

    @property
    def qdm(self) -> bool:
        if self.last_sent is None:
            return False
        return bool(self.last_sent.QDM)

    @property
    def stab(self) -> bool:
        if self.last_sent is None:
            return False
        return bool(self.last_sent.STAB)

    @property
    def launch(self) -> bool:
        if self.last_sent is None:
            return False
        return bool(self.last_sent.LAUNCH)

    @property
    def armed(self) -> bool:
        if self.last_sent is None:
            return False
        return bool(self.last_sent.ARMED)
