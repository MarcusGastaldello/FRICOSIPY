"""
    ==================================================================

                          SNOW METAMPORPHISM MODULE

        This module determines the temporal growth of the grain
        size of subsurface snow / firn layers during a single model
        timestep.

    ==================================================================
"""

import numpy as np
from constants import *
from parameters import *
from numba import njit

# ================= #
# Snow Metamorphism
# ================= #

def snow_metamorphism(GRID,dt):
    """ This module determines the metamorphism of the snowpack (snow grain growth) """

    metamorphism_allowed = ['Katsushima09', 'disabled']
    if snow_metamorphism_method == 'Katsushima09':
        method_Katsushima(GRID,dt)
    elif snow_metamorphism_method == 'disabled':
        pass
    else:
        raise ValueError("Snow Metamorphism method = \"{:s}\" is not allowed, must be one of {:s}".format(snow_metamorphism_method, ", ".join(metamorphism_allowed)))
    
    # ====================================================================================================================

    # ============================= #
    # Katsushima et al. 2009 Method
    # ============================= #

@njit
def method_Katsushima(GRID,dt):
    """ Snow grain growth based on wet snow metamorphism
        after Katsushima et al. (2009)
        (supported by the GEUS SEB firn model - Vandecrux B. - originally developed on FORTRAN by Peter Langen & Robert Fausto)
        
        Parameters:
                    dt         ::    Integration time in a model time-step [s]
        Input:
                    GRID       ::    Subsurface GRID variables -->
                    d (z)      ::    Layer grain size [mm]
                    lwc (z)    ::    Layer liquid water content [-] 
                    rho (z)    ::    Layer density [kg m-3]
                    h (z)      ::    Layer height [m]
        Output:
                    d (z)      ::    Layer grain size (updated) [mm]

    """

    # Extract variables:
    d = np.asarray(GRID.get_grain_size())
    lwc = np.asarray(GRID.get_liquid_water_content())
    rho = np.asarray(GRID.get_density())

    # Calculate gravimetric water content: [-]
    gwc = (lwc * water_density) / rho

    # Volumetric growth (according to Brun, 1989): [mm3 s-1]
    dv_Brun = 1.28e-8 + (4.22e-10 * gwc ** 3)

    # Diametric growth (according to Brun, 1989): [mm s-1]
    dd_Brun = 2 / (np.pi * d ** 2) * dv_Brun

    # Diametric growth (according to Tusima, 1978): [mm s-1]
    dd_Tusima = (2.5e-4 / d **2) * (1 / 3600)

    # Diametric growth (use Brun method if gravimetric water content below 10 %, otherwise use Tusima method) 
    dd = np.where(gwc <= 0.1 , dd_Brun, dd_Tusima)

    # Set updated grain size due to snow metamorphism:   
    GRID.set_grain_size(d + (dd * dt))

# ====================================================================================================================