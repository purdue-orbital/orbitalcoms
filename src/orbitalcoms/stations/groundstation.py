import logging
from typing import Any

from orbitalcoms.coms.messages.message import ParsableComType, construct_message

from .._utils.log import make_logger
from ..coms import ComsMessage
from .station import Station

logger = make_logger(__name__, logging.WARNING)


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
        # If armed, do not unarm
        if self.armed and not new.ARMED:
            logger.warning("Cannot unarm a station")
            return False

        # If not armed
        if not self.armed:
            # Do not abort, launch, stab, or qdm
            if new.ABORT or new.LAUNCH or new.QDM or new.STAB:
                logger.warning("Cannot do any action before arm command")
                return False

        # Do not un-arm, un-launch, or un-qdm
        if any(
            [
                not new.ABORT and self.abort,
                not new.LAUNCH and self.launch,
                not new.QDM and self.qdm,
            ]
        ):
            logger.warning("Cannot un-launch, un-abort, or un-QDM")
            return False

        # Do not launch if not stab, or have qdm/aborted
        if (
            new.LAUNCH
            and not self.launch
            and any([not self.stab, self.qdm, self.abort])
        ):
            logger.warning("Cannot launch if not stab or already abort/QDM")
            return False

        return True

    def send(self, data: ParsableComType) -> bool:
        try:
            message = construct_message(data)
            if not self._is_valid_state_change(message):
                return False
        except Exception:
            return False

        return self._is_valid_state_change(message) and super().send(message)
