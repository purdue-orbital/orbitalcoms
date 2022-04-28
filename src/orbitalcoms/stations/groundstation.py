import logging
from typing import Any

from orbitalcoms.coms.messages.message import ParsableComType, construct_message

from .._utils.log import make_logger
from ..coms import ComsMessage
from .station import Station

logger = make_logger(__name__, logging.WARNING)


class GroundStation(Station):
    def _on_receive(self, new: ComsMessage) -> Any:
        """Set data to most accurate version

        ``GroundStation`` does not have access to read mission data
        so when it recieves a message from a ``LaunchStation`` it
        assumes that data is more accurate and sets its ``_last_data``
        property appropriately

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
        if self.last_sent is None:
            return False
        return bool(self.last_sent.ABORT)

    @property
    def qdm(self) -> bool:
        """Current station QDM property

        :returns: The boolean value of the station QDM status
        :rtype: bool
        """
        if self.last_sent is None:
            return False
        return bool(self.last_sent.QDM)

    @property
    def stab(self) -> bool:
        """Current station stabilize property

        :returns: The boolean value of the station stabilize status
        :rtype: bool
        """
        if self.last_sent is None:
            return False
        return bool(self.last_sent.STAB)

    @property
    def launch(self) -> bool:
        """Current station launch property

        :returns: The boolean value of the station launch status
        :rtype: bool
        """
        if self.last_sent is None:
            return False
        return bool(self.last_sent.LAUNCH)

    @property
    def armed(self) -> bool:
        """Current station armed property

        :returns: The boolean value of the station armed status
        :rtype: bool
        """
        if self.last_sent is None:
            return False
        return bool(self.last_sent.ARMED)

    def _is_valid_state_change(self, new: ComsMessage) -> bool:
        """Validate that the message being sent is preforming a valid mission
        state change

        Because the ``GroundStation`` is responsible for the overall controll flow
        of a mission it will validate that any sent messages are making a valid
        state change for the mission. For instance a mission should not attempt
        to launch a rocket if the mission has been aborted, so if the
        ``GroundStation`` finds this inconsistency, it will return that the
        state change does not make sense.

        :param new: The message with a new mission state
        :type new: ComsMessage
        :returns: Whether or not the new mission state is valid
        :rtype: bool
        """
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
        """Validate that mission state is valid before attempting to send

        Overrides ``Station.send`` with an additional valid state
        change check

        :param data: data to format and send
        :type data: ParsableComType
        :returns: Whether or not the message was sent successfully
        :rtype: bool
        """
        try:
            message = construct_message(data)
            if not self._is_valid_state_change(message):
                return False
        except Exception:
            # FIXME: Add logging
            return False
        return self._is_valid_state_change(message) and super().send(message)
