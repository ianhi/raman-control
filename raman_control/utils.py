import numpy as np


def make_grid(N, stacked=True):
    """
    parameters
    ----------
    N : int
        number of grid points for each of x and y
    stacked : bool, optional
        if True stack x and y so that they can be directly passed
        to galvo.write
    """
    N = 100
    volts = np.linspace(-0.3, 0.3, N)
    X, Y = np.meshgrid(volts, volts)
    x = X.flatten()
    y = Y.flatten()
    if stacked:
        return np.vstack([x, y])
    return x, y
