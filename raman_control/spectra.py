from __future__ import annotations

import ctypes
import os
import time

# Import python sys module
import sys

# Import the .NET class library
import clr

# numpy import
import numpy as np

# fmt: off
# Import c compatible List and String
from System import *  # noqa
from System.Collections.Generic import List  # noqa
from System.Runtime.InteropServices import GCHandle, GCHandleType  # noqa

from .daq import DaqController
from .utils import make_grid

# Add needed dll references
sys.path.append(os.environ["LIGHTFIELD_ROOT"])
sys.path.append(os.environ["LIGHTFIELD_ROOT"] + "\\AddInViews")
clr.AddReference("PrincetonInstruments.LightFieldViewV5")
clr.AddReference("PrincetonInstruments.LightField.AutomationV5")
clr.AddReference("PrincetonInstruments.LightFieldAddInSupportServices")


from PrincetonInstruments.LightField.AddIns import *  # noqa
from PrincetonInstruments.LightField.Automation import *  # noqa

# fmt: on


class SpectraCollector:
    _instance = None

    @classmethod
    def instance(cls, lightFieldConfig: str = "Pixis_2Mhz") -> SpectraCollector:
        if cls._instance is None:
            cls._instance = cls(lightFieldConfig)
        return cls._instance

    def __init__(
        self,
        lightFieldConfig: str = "Pixis_2MHz",
        laser_controller: DaqController = None,
    ) -> None:
        self._setup_lightfield(lightFieldConfig)
        self._daq_controller = laser_controller or DaqController.instance()

    @property
    def daq(self) -> DaqController:
        return self._daq_controller

    def remove_filter(self, wait: int = 4000):
        """
        Remove the Focus filter to allow raman

        Parameters
        ----------
        wait : int
            How long to wait for the acututor to finish moving in ms.
        """
        self._daq_controller.remove_filter()
        time.sleep(wait)

    def insert_filter(self, wait: int = 4000):
        """
        Insert the Focus filter to allow raman autofocus

        Parameters
        ----------
        wait : int
            How long to wait for the acututor to finish moving in ms.
        """
        self._daq_controller.insert_filter()
        time.sleep(wait)

    @staticmethod
    def _convert_buffer(net_array, image_format):
        src_hndl = GCHandle.Alloc(net_array, GCHandleType.Pinned)
        try:
            src_ptr = src_hndl.AddrOfPinnedObject().ToInt64()

            # Possible data types returned from acquisition
            if image_format == ImageDataFormat.MonochromeUnsigned16:
                buf_type = ctypes.c_ushort * len(net_array)
            elif image_format == ImageDataFormat.MonochromeUnsigned32:
                buf_type = ctypes.c_uint * len(net_array)
            elif image_format == ImageDataFormat.MonochromeFloating32:
                buf_type = ctypes.c_float * len(net_array)

            cbuf = buf_type.from_address(src_ptr)
            resultArray = np.frombuffer(cbuf, dtype=cbuf._type_)

        # Free the handle
        finally:
            if src_hndl.IsAllocated:
                src_hndl.Free()

        # Make a copy of the buffer
        return np.copy(resultArray)

    def _convert_capture(self, cap, spectrum_length=1340):
        """
        parameters
        ----------
        cap : experiment.Capture
        spectrum_length : int
            1340 for current setup

        returns
        -------
        numpy array
            rows are samples
        """
        arr = np.zeros([cap.Frames, spectrum_length], dtype=np.uint16)
        for i in range(cap.Frames):
            frame = cap.GetFrame(0, i)
            arr[i] = self._convert_buffer(frame.GetData(), frame.Format)
        return arr

    def _setup_lightfield(self, config: str):
        """
        Start and set up lightfield.
        usage
        -----
        auto, experiment, set_value, set_rm_exposure = setup_lightfield()
        """
        # Create the LightField Application (true for visible)
        # The 2nd parameter forces LF to load with no experiment
        auto = Automation(True, List[String]())
        experiment = auto.LightFieldApplication.Experiment
        experiment.Load(config)

        self._auto = auto
        self._experiment = experiment

    def _set_value(self, setting, value):
        # Check for existence before setting
        # gain, adc rate, or adc quality
        if self._experiment.Exists(setting):
            self._experiment.SetValue(setting, value)

    def set_rm_exposure(self, exposure: float):
        """
        Sets the exposure time for raman

        Parameters
        ----------
        exposure : float
            camera exposure in milliseconds
        """
        self._set_value(CameraSettings.ShutterTimingExposureTime, exposure)

    def collect_spectra(self, points, exposure=20):
        """
        Parameters
        ----------
        points : arraylike
            shape (2, N)
        exposure : float (Default: 20)
            exposure time in ms

        Returns
        -------
        spectra : array
            with shape (N, 1340)
        """
        points = np.asarray(points)
        self.set_rm_exposure(exposure)

        self._daq_controller.prepare_for_collection(points)
        self._experiment.Stop()
        with self._daq_controller.open_shutter:
            dataset = self._experiment.Capture(points.shape[1])
        self._daq_controller.galvo.stop()
        return self._convert_capture(dataset)

    def capture_rm_grid(
        self,
        N: int = 75,
        exposure: float = 20,
        min_volts: float = -0.6,
        max_volts: float = 0.6,
    ):
        """
        Collect a uniform grid of raman spectra.

        Parameters
        ----------
        N : int
            Length of the grid sides
        exposure : float
            exposure time in ms
        min_volts, max_volts : float
            The max voltage to apply to the galvos

        Returns
        -------
        spectra : array
            shape (N, N, 1340)
        volts : 1D array
            volts for passing to laser-pointer
        """
        xy_grid, volts = make_grid(N, min_volts, max_volts, stacked=True)
        return (
            self.collect_spectra(xy_grid, exposure).squeeze().reshape(N, N, 1340),
            volts,
        )

    def close(self):
        """Properly close open resources"""
        self._daq_controller.close()
        self._experiment.Stop()
        self._auto.Dispose()
