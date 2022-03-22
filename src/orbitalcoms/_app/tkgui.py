"""Ugly, inefficent, and all round grabage gui in tkinter
for testing, mocking, and debuging purposes

TODO: Replace with something better ASAP
"""
from __future__ import annotations

import json
import tkinter as tk
from typing import TYPE_CHECKING, Any
import datetime

from orbitalcoms.coms.messages.message import ComsMessage

if TYPE_CHECKING:
    from ..stations.groundstation import GroundStation


class GroundStationFrame(tk.Frame):
    class FrameUpdateQueue:
        def __init__(self, gui: GroundStationFrame) -> None:
            self._gui = gui

        def append(self, _: Any) -> None:
            self._gui.update_disp()

    def __init__(self, gs: GroundStation, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._gs = gs
        self._gs.bind_queue(GroundStationFrame.FrameUpdateQueue(self))
        self.grid(column=0, row=0, sticky="nsew")
        self.master.columnconfigure(index=0, weight=1)
        self.master.rowconfigure(index=0, weight=1)

        self.columnconfigure(index=0, weight=1, uniform="1")
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1)
        self.rowconfigure(index=2, weight=1)
        self.rowconfigure(index=3, weight=1)
        self.rowconfigure(index=4, weight=1)

        self.columnconfigure(index=1, weight=1, uniform="1")
        self.columnconfigure(index=2, weight=1, uniform="1")
        self.columnconfigure(index=3, weight=1, uniform="1")

        # Buttons
        self.btn_arm = tk.Button(
            self, text="ARM", command=lambda: self.send_state("ARMED")
        )
        self.btn_abort = tk.Button(
            self, text="ABORT", command=lambda: self.send_state("ABORT")
        )
        self.btn_qdm = tk.Button(
            self, text="QDM", command=lambda: self.send_state("QDM")
        )
        self.btn_stab = tk.Button(
            self, text="STABILIZE", command=lambda: self.send_state("STAB")
        )
        self.btn_launch = tk.Button(
            self, text="LAUNCH", command=lambda: self.send_state("LAUNCH")
        )

        self.btn_arm.grid(column=0, row=0, sticky="nsew")
        self.btn_abort.grid(column=0, row=1, sticky="nsew")
        self.btn_qdm.grid(column=0, row=2, sticky="nsew")
        self.btn_stab.grid(column=0, row=3, sticky="nsew")
        self.btn_launch.grid(column=0, row=4, sticky="nsew")

        # Text
        self.txt_sent = tk.Text(self)
        self.txt_recv = tk.Text(self)
        self.txt_data = tk.Text(self)

        self.txt_sent.grid(column=1, row=0, rowspan=5, sticky="nsew")
        self.txt_recv.grid(column=2, row=0, rowspan=5, sticky="nsew")
        self.txt_data.grid(column=3, row=0, rowspan=5, sticky="nsew")

        self.update_disp()

    def send_state(self, update: str) -> None:
        state = (
            self._gs.last_sent.as_dict
            if self._gs.last_sent
            else ComsMessage(0, 0, 0, 0).as_dict
        )
        state[update] = 0 if state[update] else 1
        self._gs.send(state)
        self.update_disp()

    def update_disp(self) -> None:
        def coms_msg_txt_fomat(msg: ComsMessage | None, title: str = "") -> str:
            if title:
                title = f"{title}:\n" + "=" * len(title) + "\n"
            if msg is None:
                return f"{title}null"
            return title + (
                f"ARMED:  {msg.ARMED}\n"
                f"ABORT:  {msg.ABORT}\n"
                f"QDM:    {msg.QDM}\n"
                f"STAB:   {msg.STAB}\n"
                f"LAUNCH: {msg.LAUNCH}\n"
            )

        def make_time_stamp(time: float | None) -> datetime.datetime | str:
            if time:
                return datetime.datetime.fromtimestamp(time)
            return "None"
        self.txt_sent.delete(1.0, "end")
        self.txt_sent.insert(
            1.0,
            coms_msg_txt_fomat(self._gs.last_sent, "SENT")
            + f"\n\nTime Sent: {make_time_stamp(self._gs.last_sent_time)}",
        )

        self.txt_recv.delete(1.0, "end")
        self.txt_recv.insert(
            1.0,
            coms_msg_txt_fomat(self._gs.last_received, "RECV")
            + f"\n\nTime Recv: {make_time_stamp(self._gs.last_received_time)}",
        )

        self.txt_data.delete(1.0, "end")
        try:
            data_str = json.dumps(self._gs.data, indent=2)
        except Exception:
            data_str = str(self._gs.data)
        self.txt_data.insert(1.0, f"DATA:\n====\n{data_str}")


def run_app(gs: GroundStation) -> None:
    root = tk.Tk()
    root.title("Development GS GUI")
    width = 800
    height = 600
    root.geometry(f"{width}x{height}")
    gs_gui = GroundStationFrame(gs, master=root)
    gs_gui.mainloop()
