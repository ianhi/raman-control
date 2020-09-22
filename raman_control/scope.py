import numpy as np

from pycromanager import Bridge


def setup_scope():
    """
    Setup connection to μmanager and create convenience functions

    usage
    -----
    bridge, core, snap_image = setup_scope()
    """
    bridge = Bridge()
    core = bridge.get_core()

    def snap_image():
        """
        wrapper around core.snap_image to return a reshaped numpy array
        """
        core.snap_image()
        tagged_image = core.get_tagged_image()
        return np.reshape(
            tagged_image.pix,
            newshape=[tagged_image.tags["Height"], tagged_image.tags["Width"]],
        )

    return bridge, core, snap_image