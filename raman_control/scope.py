import numpy as np

from pycromanager import Bridge
import json


def setup_scope():
    """
    Setup connection to μmanager and create convenience functions

    usage
    -----
    bridge, core, snap_image, collect_bf_images = setup_scope()
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

    def collect_bf_images(xy, z=None):
        """
        parameters
        ---------
        xy : arraylike 2D
        z : arraylike or None
        """
        ims = []
        for i in range(len(xy)):
            core.set_xy_position(*xy[i])
            if z is not None:
                core.set_position(z[i])
            ims.append(snap_image())
        return np.asarray(ims)

    return bridge, core, snap_image, collect_bf_images


def position_file_to_coords(fname):
    """
    parameters
    ----------
    fname : str
        The path the to the .pos from μmanager

    returns
    -------
    XY : 2D array
    Z : 1D array
    """
    with open(fname) as f:
        positions = json.load(f)
    xyz = positions["map"]["StagePositions"]["array"]
    pos = xyz[0]["DevicePositions"]["array"]
    X = []
    Y = []
    Z = []
    for i in range(len(xyz)):
        pos = xyz[i]["DevicePositions"]["array"]
        for i, p in enumerate(pos):
            device = p["Device"]
            if "FocusDrive" == device["scalar"]:
                # z
                z = p["Position_um"]["array"][0]
            elif "XYStage" == device["scalar"]:
                # xy
                x, y = p["Position_um"]["array"]
        X.append(x)
        Y.append(y)
        Z.append(z)
    xy_pos = np.zeros([len(X), 2])
    xy_pos[:, 0] = X
    xy_pos[:, 1] = Y
    return xy_pos, np.asarray(Z)
