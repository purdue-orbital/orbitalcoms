"""Headless frontend to ensure that the orbitalcoms package can be used
in a purely terminal based enviornment
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

if TYPE_CHECKING:
    from orbitalcoms.stations.groundstation import GroundStation


class GSKeyboardControl:
    def __init__(self, gs: GroundStation) -> None:
        self._gs = gs

    def on_press(self, key: KeyCode | Key | None) -> bool:
        return True

    def on_release(self, key: KeyCode | Key | None) -> bool:
        if key == Key.esc:
            # Stop the listener
            return False
        if isinstance(key, KeyCode):
            if key.char == "a":
                return True
            if key.char == "l":
                return True
            if key.char == "q":
                return True
            if key.char == "r":
                return True
            if key.char == "s":
                return True
        print(f"Unhandled Input Key: {key}")
        return True


def run_app(gs: GroundStation) -> None:
    keyboard_ctrl = GSKeyboardControl(gs)
    with keyboard.Listener(
        on_press=keyboard_ctrl.on_press, on_release=keyboard_ctrl.on_release
    ) as listener:
        listener.join()
