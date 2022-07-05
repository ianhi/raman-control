from __future__ import annotations
import numpy as np
from sklearn import linear_model
from numpy.polynomial.polynomial import polyvander2d as vander2d
import json
from pathlib import Path


class CoordTransformer:
    def __init__(
        self, coef: np.ndarray, intercept: np.ndarray, vander_degs: tuple[int, int]
    ):
        """
        Parameters
        ----------
        coef : (2, N) array-like
            The coefficients of the linear model
        intercept : float
        vander_degs : (int, int)
            The degrees to use for the vandermonde matrix
        """
        self._coef = coef
        self._intercept = intercept
        self._vander_degs = vander_degs

    def BF_to_RM(self, X: np.ndarray, Y: np.ndarray = None) -> np.ndarray:
        """
        Transform from relative BF [0, 1] to relative Raman coordinates [0, 1]

        Parameters
        -----------
        X : (N, [2]) array-like
        Y : (N,) array-like, optional
            Only necessary if X is not 2D

        Returns
        -------
        positions (N, 2)
            The positions as Ram
        """
        X = np.asanyarray(X)
        if X.ndim == 2:
            Y = X[:, 1]
            X = X[:, 0]
        vander = vander2d(X, Y, self._vander_degs)
        return vander @ self._coef.T + self._intercept

    def RM_to_volts(
        self, X: np.ndarray, Y: np.ndarray = None, max_volts: float = 0.6
    ) -> np.ndarray:
        """
        Transform from relative RM [0, 1] to galvo voltages, e.g. [-.6, .6].  Parameters
        -----------
        X : (N, [2]) array-like
        Y : (N,) array-like, optional
            Only necessary if X is not 2D
        max_volts : float, default .6
            The voltage corresponding to maximal voltage used when generating the model.

        Returns
        -------
        volts : (N, 2)
        """
        X = np.asarray(X)
        if X.ndim != 2:
            X = np.column_stack([X, Y])
        return 2*max_volts * X - max_volts

    def BF_to_volts(
        self, X: np.ndarray, Y: np.ndarray = None, max_volts: float = 0.6
    ) -> np.ndarray:
        """
        Transform from relative BF [0, 1] to relative Raman coordinates [0, 1]

        Parameters
        -----------
        X : (N, [2]) array-like
        Y : (N,) array-like, optional
            Only necessary if X is not 2D
        max_volts : float, default .6
            The voltage corresponding to maximal voltage used when generating the model.

        Returns
        -------
        positions (N, 2)
            The positions as galvo voltages
        """
        return self.RM_to_volts(self.BF_to_RM(X, Y), max_volts=max_volts)

    @staticmethod
    def fit_model(
        rel_BF: np.ndarray,
        rel_RM: np.ndarray,
        vander_degs: tuple[int, int] = (3, 3),
        alpha: float = 0.05,
    ):
        """
        Fit a model mapping from relative BF space to relative RM space.

        Parameters
        ----------
        rel_BF, rel_RM : (N, 2) array-like
            The positions of shared points (e.g. beads) in relative coords [0, 1]
        vander_degs : (int, int)
            The x and y degrees of the vandermonde matrix
        alpha : float, default 0.05
            The alpha of the Ridge model.

        Returns
        -------
        sklearn.linear_model.Ridge
        """
        model = linear_model.Ridge(alpha=alpha)
        vander = vander2d(rel_BF[:,0],rel_BF[:,1], vander_degs)
        model.fit(vander, rel_RM)
        return model

    @staticmethod
    def save_model(
        savename: str,
        model: linear_model.Ridge,
        vander_degs: tuple[int, int],
        metadata: dict = {},
        **kwargs
    ):
        """
        Save the model and vandermonde info as a json file.

        Parameters
        ----------
        savename : str
        model : sklearn.linear_model.Ridge
            The fit model
        vander_degs : (int, int)
            The vandermonde degrees
        metadata : dict
            Arbitrary (json-serializable) metadata
        **kwargs
            Added to the metadata
        """
        metadata = {**metadata, **kwargs}
        info = {
            "metadata": metadata,
            "vander_degs": vander_degs,
            "coef": model.coef_.tolist(),
            "intercept": model.intercept_.tolist(),
        }

        with open(savename, "w") as f:
            json.dump(info, f)

    @staticmethod
    def from_json(fname: str=None):
        """
        Generate a CoordTransformer from a json file.

        Parameters
        ----------
        fname : str, optional
            The name of the json file. If not provided then load the default model
            distributed with the package.

        Returns
        -------
        CoordTransformer
        """
        if fname is None:
            fname = str(Path(__file__).parent / "model.json")
        with open(fname, "r") as f:
            info = json.load(f)
        return CoordTransformer(
            np.array(info["coef"]),
            np.array(info["intercept"]),
            info["vander_degs"],
        )
    
