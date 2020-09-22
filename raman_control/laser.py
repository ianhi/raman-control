import nidaqmx
import numpy as np

SAMPLERATE = 100000


class shutter_controller:
    def __init__(self, shutter, open_):
        self.shutter = shutter
        self.open_ = open_

    def __enter__(self):
        self.shutter.write(self.open_)

    def __exit__(self, *exc):
        self.shutter.write(not self.open_)

    def __call__(self):
        self.shutter.write(self.open_)


def setup_laser_control(
    sampleClockSource="PFI0",
    devName="Dev1",
    channels=["Dev1/ao0", "Dev1/ao1"],
):

    # galvo mirror
    galvo = nidaqmx.Task("galvoAO")
    galvo.ao_channels.add_ao_voltage_chan(channels[0], "x", min_val=-10, max_val=10)
    galvo.ao_channels.add_ao_voltage_chan(channels[1], "y", min_val=-10, max_val=10)

    # laser shutter
    shutter = nidaqmx.Task("shutterDO")
    shutter_chan = shutter.do_channels.add_do_chan("Dev1/port0/line0")

    open_shutter = shutter_controller(shutter, True)
    close_shutter = shutter_controller(shutter, False)
    shutter.open = open_shutter
    shutter.close = close_shutter

    def close_daq():
        """
        stop then close the galvo and shutter daq connections
        """
        shutter.stop()
        shutter.close()
        galvo.stop()
        galvo.close()

    return galvo, shutter, open_shutter, close_shutter, close_daq
