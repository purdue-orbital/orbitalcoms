"""Ugly and simple gui for testing and debug
purposes using tkinter
"""
from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..stations.groundstation import GroundStation


class GroundStationFrame(tk.Frame):
    def __init__(self, gs: GroundStation, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._gs = gs
        self.grid(column=0, row=0, sticky="nsew")
        self.master.columnconfigure(index=0, weight=1)
        self.master.rowconfigure(index=0, weight=1)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1)
        self.rowconfigure(index=2, weight=1)
        self.rowconfigure(index=3, weight=1)
        self.rowconfigure(index=4, weight=1)

        # Buttons
        self.btn_arm = tk.Button(self, text="ARM")
        self.btn_abort = tk.Button(self, text="ABORT")
        self.btn_qdm = tk.Button(self, text="QDM")
        self.btn_stab = tk.Button(self, text="STABALIZE")
        self.btn_launch = tk.Button(self, text="LAUNCH")

        self.btn_arm.grid(column=0, row=0, sticky="nsew")
        self.btn_abort.grid(column=0, row=1, sticky="nsew")
        self.btn_qdm.grid(column=0, row=2, sticky="nsew")
        self.btn_stab.grid(column=0, row=3, sticky="nsew")
        self.btn_launch.grid(column=0, row=4, sticky="nsew")

        # Message Frames

        # Data Frame


def run_app(gs: GroundStation) -> None:
    root = tk.Tk()
    gs_gui = GroundStationFrame(gs, master=root)
    gs_gui.mainloop()


if __name__ == "__main__":
    from ..coms.drivers.localcomsdriver import LocalComsDriver
    from ..stations.groundstation import GroundStation  # noqa: F811, will be removed

    run_app(GroundStation(LocalComsDriver()))
