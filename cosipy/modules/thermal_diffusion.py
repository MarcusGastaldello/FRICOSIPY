import numpy as np
from numba import njit
from constants import *
from parameters import *

# ===================================================================================== #
@njit
def thermal_diffusion(GRID, BASAL, dt):
    """ This function solves the one-dimensional heat equation through the subsurface 
        layers T(z) using a first order, finite, central difference scheme:

        Constants:
                    dt = 3600       Integration time in a model time-step (hour) [s]
        Input:
                    h(z):           Layer height [m]
                    K(z):           Layer thermal diffusivity [m2 s-1]
                    k(z):           Layer thermal conductivity [W m-1 K-1]
                    T(z):           Layer temperature [K]
                    BASAL:          Basal heat flux [mW m-2]
        Output:
                    T(z):           Layer temperature (updated) [K]
    """

    basal_heat_flux = BASAL * (45 / 35) / 1000
    z = np.asarray(GRID.get_height())
    K = np.asarray(GRID.get_thermal_diffusivity())
    T = np.asarray(GRID.get_temperature())
    k = np.asarray(GRID.get_thermal_conductivity())
    Tnew = T.copy()

    # =============================================================================
    # Numerically Solve the Heat Equation using a Finite Central Difference Scheme:
    # =============================================================================

    # Determine integration steps required in the solver to ensure numerical stability:
    dt_stable = 0.5 * min(((z[1:] + z[:-1]) / 2)**2 / ((K[1:] + K[:-1]) / 2)) # Von Neumann Stability Condition
    dt_cumulative = 0.0 

    while dt_cumulative < dt:

        dt_step = np.minimum(dt_stable, dt - dt_cumulative)
        dt_cumulative += dt_step

        # Update the temperatures
        Tnew[1:-1] = T[1:-1] + dt_step * (((0.5 * (K[2:]  + K[1:-1]))  * (T[2:]   - T[1:-1]) / (0.5 * (z[2:]  + z[1:-1])) - \
                                           (0.5 * (K[:-2] + K[1:-1]))  * (T[1:-1] - T[:-2])  / (0.5 * (z[:-2] + z[1:-1]))) / \
                                           (0.25 * z[:-2]  + 0.5 * z[1:-1] + 0.25 * z[2:]))
        Tnew[-1]   = T[-1]   + dt_step * (((basal_heat_flux * K[-1] / k[-1]) - \
                                          ((0.5 * (K[-2] + K[-1])) * (T[-1] - T[-2])  / (0.5 * (z[-2] + z[-1])))) / \
                                           (0.25 * z[-2] + 0.75 * z[-1]))
        T = Tnew.copy()

    # Write results to GRID
    GRID.set_temperature(T)