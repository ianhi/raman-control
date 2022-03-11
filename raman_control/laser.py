from __future__ import annotations
import nidaqmx

from typing import List
import numpy as np

SAMPLERATE = 100000

__all__ = [
    "DigitalStateContextManager",
    "LaserController",
]


class DigitalStateContextManager:
    def __init__(self, shutter, open_):
        self.shutter = shutter
        self.open_ = open_

    def __enter__(self):
        self.shutter.write(self.open_)

    def __exit__(self, *exc):
        self.shutter.write(not self.open_)

    def __call__(self):
        self.shutter.write(self.open_)


class LaserController:
    _instance = None

    @classmethod
    def instance(
        cls,
        sampleClockSource: str = "PFI0",
        devName: str = "Dev1",
        channels: List[str] = ["Dev1/ao0", "Dev1/ao1"],
    ) -> LaserController:
        if cls._instance is None:
            cls._instance = cls(sampleClockSource, devName, channels)
        return cls._instance

    def __init__(
        self, sampleClockSource="PFI0", devName="Dev1", channels=["Dev1/ao0", "Dev1/ao1"]
    ) -> None:
        # galvo mirror
        self._galvo = nidaqmx.Task("galvoAO")
        self._galvo.ao_channels.add_ao_voltage_chan(
            channels[0], "x", min_val=-10, max_val=10
        )
        self._galvo.ao_channels.add_ao_voltage_chan(
            channels[1], "y", min_val=-10, max_val=10
        )

        # laser shutter
        self._shutter = nidaqmx.Task("shutterDO")
        # not sure if this next line does anything or is important
        self._shutter.do_channels.add_do_chan("Dev1/port0/line0")
        self._open_shutter = DigitalStateContextManager(self._shutter, True)
        self._close_shutter = DigitalStateContextManager(self._shutter, False)
        # shutter.open = open_shutter
        # shutter.close = close_shutter

    @property
    def open_shutter(self) -> DigitalStateContextManager:
        return self._open_shutter

    @property
    def close_shutter(self) -> DigitalStateContextManager:
        return self._close_shutter

    @property
    def galvo(self) -> nidaqmx.Task:
        return self._galvo

    def close(self):
        """
        stop then close the galvo and shutter daq connections
        """
        self._shutter.stop()
        self._shutter.close()
        self._galvo.stop()
        self._galvo.close()

    def prepare_for_collection(self, points: np.ndarray):
        """
        Set up the galvo to aim at positions on camera frames.

        Parameters
        ----------
        points : 2xN array
        """
        self._galvo.stop()
        # xy_grid, volts = make_grid(N)
        SAMPLERATE = 100000
        SAMPLECLOCKSOURCE = "PFI0"
        self._galvo.timing.cfg_samp_clk_timing(
            SAMPLERATE,
            source=SAMPLECLOCKSOURCE,
            active_edge=nidaqmx.constants.Edge.FALLING,
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=points.shape[1],
        )
        self._galvo.write(points, auto_start=False)
