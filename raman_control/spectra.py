# Import the .NET class library
import clr, ctypes

# Import python sys module
import sys, os

# numpy import
import numpy as np

# Import c compatible List and String
from System import *
from System.Collections.Generic import List
from System.Runtime.InteropServices import Marshal
from System.Runtime.InteropServices import GCHandle, GCHandleType


# Add needed dll references
sys.path.append(os.environ["LIGHTFIELD_ROOT"])
sys.path.append(os.environ["LIGHTFIELD_ROOT"] + "\\AddInViews")
clr.AddReference("PrincetonInstruments.LightFieldViewV5")
clr.AddReference("PrincetonInstruments.LightField.AutomationV5")
clr.AddReference("PrincetonInstruments.LightFieldAddInSupportServices")

# PI imports
from PrincetonInstruments.LightField.Automation import *
from PrincetonInstruments.LightField.AddIns import *


def convert_buffer(net_array, image_format):
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


def convert_capture(cap, spectrum_length=1340):
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
    arr = np.zeros([cap.Frames, 1340], dtype=np.uint16)
    for i in range(cap.Frames):
        frame = cap.GetFrame(0, i)
        arr[i] = convert_buffer(frame.GetData(), frame.Format)
    return arr


def setup_camera():
    """
    Start and set up lightfield.
    usage
    -----
    auto, experiment, set_value, set_rm_exposure = setup_camera()
    """
    # Create the LightField Application (true for visible)
    # The 2nd parameter forces LF to load with no experiment
    auto = Automation(True, List[String]())
    experiment = auto.LightFieldApplication.Experiment
    experiment.Load("Pixis")

    def set_value(setting, value):
        # Check for existence before setting
        # gain, adc rate, or adc quality
        if experiment.Exists(setting):
            experiment.SetValue(setting, value)

    def set_rm_exposure(exposure_time):
        """
        sets the exposure time for raman
        parameters
        ----------
        exposure_time : float
            camera exposure in milliseconds
        """
        return set_value(CameraSettings.ShutterTimingExposureTime, exposure_time)

    return auto, experiment, set_value, set_rm_exposure
