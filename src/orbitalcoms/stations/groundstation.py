from typing import Any

from orbitalcoms.coms.messages.message import ParsableComType, construct_message

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

    def _is_valid_state_change(self, new: ComsMessage) -> bool:
        if self._last_sent is not None:
            return all(
                [
                    self.armed and not self.abort if self.abort != new.ABORT else True,
                    not self.armed if self.armed != new.ARMED else True,
                    self.armed
                    and not self.abort
                    and not self.qdm
                    and not self.launch
                    and self.stab
                    if self.launch != new.LAUNCH
                    else True,
                    self.armed and not self.qdm if self.qdm != new.QDM else True,
                    self.armed if self.stab != new.STAB else True,
                ]
            )
        else:
            return bool(new.ARMED)

    def send(self, data: ParsableComType) -> bool:
        try:
            message = construct_message(data)
            if not self._is_valid_state_change(message):
                return False
            
            # if self._timeout_thread.is_alive():
            #     self._timeout_thread.stop()
            # self._timeout_thread = self.StoppableThread(self.resend_last)
            # self._timeout_thread.start()
        except Exception: 
            return False

        return self._is_valid_state_change(message) and super().send(message)
