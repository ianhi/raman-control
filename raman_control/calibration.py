import matplotlib.pyplot as plt
from laser_pointer import fit_transform_pointers


def create_calibrate(capture_rm_grid, snap_image, lp):
    """
    Parameters
    ----------
    capture_rm_grid : function
    snap_image : function
    lp : the laser_pointer module

    returns
    -------
    calibrate : function
    """

    def calibrate(N=75, exposure=20):
        """
        fit_calibration, lp_bf, lp_rm = calibrate()

        Parameters
        ----------
        N : int
            Dimension of the laser grid
        exposure : float
            Exposure time in ms

        Returns
        -------
        fit_calibration : function
            to be called when an adequate number of points have been selected
        lp_bf
        lp_rm
        """
        bf = snap_image()
        rm, volts = capture_rm_grid(N, exposure)
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        lp_bf = lp.pointer(bf, axes[0])
        lp_rm = lp.pointer(rm[:, :, 664], axes[1], X=volts, Y=volts, radius=0.005)

        def fit_calibration(plot=True):
            """
            Usage
            -----
            ```
            (
                transform_pointer,
                bfx_to_rmx,
                bfy_to_rmy,
                inverse_x,
                inverse_y,
            ) = fit_calibration()
            ```
            """
            return fit_transform_pointers(lp_bf, lp_rm)

        return fit_calibration, lp_bf, lp_rm

    return calibrate
