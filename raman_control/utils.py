import numpy as np


def make_grid(N, min_volts: float = -0.3, max_volts: float = 0.3, *, stacked=True):
    """

    Parameters
    ----------
    N : int
        number of grid points for each of x and y
    min_volts, max_volts : float
        Between -.6 and .6
    stacked : bool, optional
        if True stack x and y so that they can be directly passed
        to galvo.write

    Returns
    -------
    xy, volts
    or
    x, y, volts
    """
    if np.abs(min_volts) > 0.6 or np.abs(max_volts) > 0.6:
        raise ValueError("voltage must inside [-0.6, 0.6] volts.")

    volts = np.linspace(min_volts, max_volts, N)
    X, Y = np.meshgrid(volts, volts)
    x = X.flatten()
    y = Y.flatten()
    if stacked:
        return np.vstack([x[:, None], y[:, None]]), volts
    return x, y, volts
