"""Headless frontend to ensure that the orbitalcoms package can be used
in a purely terminal based enviornment
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from orbitalcoms.coms.messages.message import ComsMessage

from ..coms import messages

if TYPE_CHECKING:
    from orbitalcoms.stations.groundstation import GroundStation


class GSKeyboardControl:
    def __init__(self, gs: GroundStation) -> None:
        self._gs = gs
        self._gs.bind_queue(GSKeyboardControl.DisplayUpdater())

    def on_press(self, key: KeyCode | Key | None) -> bool:
        return True

    def on_release(self, key: KeyCode | Key | None) -> bool:
        if key == Key.esc:
            # Stop the listener
            return False
        if isinstance(key, KeyCode):
            if key.char == "a":
                m = messages.construct_message(
                    {
                        "ABORT": not self._gs.abort,
                        "QDM": self._gs.qdm,
                        "STAB": self._gs.stab,
                        "LAUNCH": self._gs.launch,
                        "ARMED": self._gs.armed,
                        "DATA": self._gs.data,
                    }
                )
                self._gs.send(m)
                return True
            if key.char == "l":
                m = messages.construct_message(
                    {
                        "ABORT": self._gs.abort,
                        "QDM": self._gs.qdm,
                        "STAB": self._gs.stab,
                        "LAUNCH": not self._gs.launch,
                        "ARMED": self._gs.armed,
                        "DATA": self._gs.data,
                    }
                )
                self._gs.send(m)
                return True
            if key.char == "q":
                m = messages.construct_message(
                    {
                        "ABORT": self._gs.abort,
                        "QDM": not self._gs.qdm,
                        "STAB": self._gs.stab,
                        "LAUNCH": self._gs.launch,
                        "ARMED": self._gs.armed,
                        "DATA": self._gs.data,
                    }
                )
                self._gs.send(m)
                return True
            if key.char == "r":
                m = messages.construct_message(
                    {
                        "ABORT": self._gs.abort,
                        "QDM": self._gs.qdm,
                        "STAB": self._gs.stab,
                        "LAUNCH": self._gs.launch,
                        "ARMED": not self._gs.armed,
                        "DATA": self._gs.data,
                    }
                )
                self._gs.send(m)
                return True
            if key.char == "s":
                m = messages.construct_message(
                    {
                        "ABORT": self._gs.abort,
                        "QDM": self._gs.qdm,
                        "STAB": not self._gs.stab,
                        "LAUNCH": self._gs.launch,
                        "ARMED": self._gs.armed,
                        "DATA": self._gs.data,
                    }
                )
                self._gs.send(m)
                return True
        print(f"Unhandled Input Key: {key}")
        return True

    class DisplayUpdater:
        def append(self, m: ComsMessage) -> None:
            print(
                (
                    "===============================\n"
                    "Received New Message:\n"
                    "===============================\n"
                    f"ARMED:  {m.ARMED}\n"
                    f"ABORT:  {m.ABORT}\n"
                    f"QDM:    {m.QDM}\n"
                    f"STAB:   {m.STAB}\n"
                    f"LAUNCH: {m.LAUNCH}\n"
                    "===============================\n"
                )
            )


def run_app(gs: GroundStation) -> None:
    keyboard_ctrl = GSKeyboardControl(gs)
    with keyboard.Listener(
        on_press=keyboard_ctrl.on_press, on_release=keyboard_ctrl.on_release
    ) as listener:
        listener.join()
