import numpy as np


def make_grid(N, stacked=True, min_volts=-0.3, max_volts=0.3):
    """
    parameters
    ----------
    N : int
        number of grid points for each of x and y
    stacked : bool, optional
        if True stack x and y so that they can be directly passed
        to galvo.write
    returns
    -------
    xy, volts
    or
    x, y, volts
    """
    volts = np.linspace(min_volts, max_volts, N)
    X, Y = np.meshgrid(volts, volts)
    x = X.flatten()
    y = Y.flatten()
    if stacked:
        return np.vstack([x, y]), volts
    return x, y, volts
