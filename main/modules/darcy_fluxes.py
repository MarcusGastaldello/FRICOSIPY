"""
    ==================================================================

                          DARCY FLUXES MODULE

        This module calculates the (water) mass fluxes between 
        subsurface layers according to Darcy's law - the equation 
        governing fluid flow through a porous medium (snow).

        This code was implemented into FRICOSIPY from the Geological 
        Survey of Denmark and Greenland (GEUS) SEB Firn model of
        Baptiste Vandecrux (bav@geus.dk), although it was originally 
        developed by Peter Langen (pla@dmi.dk) and Robert S. Fausto
        (rsf@geus.dk) in the FORTRAN programming language.

    ==================================================================
"""

import numpy as np
from numba import njit
from constants import *
from parameters import *

# ============ #
# Darcy Fluxes
# ============ #

@njit
def darcy_fluxes(GRID, dt):
    """ This module calculates the mass fluxes (of liquid water) between subsurface layers calculated according
        to the Darcy law for fluid flow through a porous medium (snow)
        according to Hirashima et al., (2010) (https://doi.org/10.1016/j.coldregions.2010.09.003)

        Input:
                    GRID     ::    Subsurface GRID variables -->
                    lwc      ::    Layer liquid water content [-] 
                    irr      ::    Layer irreducible water content [-] 
                    icf      ::    Layer ice fraction [-] 
                    d        ::    Layer grain size [mm]
                    z        ::    Layer height [m]
                    h        ::    Layer hydraulic head [m]
                    K        ::    Layer hydraulic conductivity []

        Output:     D (z)    ::    Darcy fluxes [m w.e.]    

    """

    # Initialise Darcy fluxes array:
    D = np.zeros(GRID.number_nodes)

    # Loop over all internal sub-surface grid nodes:
    for Idx in range(0, GRID.number_nodes - 1):

        # Calculate the water flux limit (q_lim):
        q_lim = water_flux_q_lim(GRID, Idx)

        # Calculate midpoint-to-midpoint distance between layers:
        dz = (GRID.get_node_height(Idx) + GRID.get_node_height(Idx + 1)) / 2

        # Hydraulic gradient (dh/dz):
        dhdz = (GRID.get_node_hydraulic_head(Idx + 1) - GRID.get_node_hydraulic_head(Idx)) / dz

        # Hydraulic conductivity (K):
        K = (GRID.get_node_hydraulic_conductivity(Idx) + GRID.get_node_hydraulic_conductivity(Idx + 1)) / 2

        # Initial water flux (q0): Hirashima et al. (2010) Eq. (1)
        q0 = max(K * (dhdz + 1), 0)

        # Calculate total water flux for model integration timestep: Hirashima et al. (2010) Eq. (23)
        # (ensuring the flux does not exceed the water content of the upper layer!)
        if q_lim > 0:
            D[Idx] = min(GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx), q_lim * (1 - np.exp(- q0 / q_lim * dt)))
        else:
            D[Idx] = 0
    
    return D

# ====================================================================================================================

# ================== #
# Water Flux (q_lim)
# ================== #

@njit
def water_flux_q_lim(GRID, Idx):
    """ Iteratively determines the water flux limit between an upper (Idx) and lower (Idx + 1) subsurface layer
        according to Hirashima et al., (2010) (https://doi.org/10.1016/j.coldregions.2010.09.003) - Eq. 20)

        Input:
                    GRID     ::    Subsurface GRID variables -->
                    lwc      ::    Layer liquid water content [-] 
                    irr      ::    Layer irreducible water content [-] 
                    icf      ::    Layer ice fraction [-] 
                    d        ::    Layer grain size [mm] 

        Output:
                    q_lim    ::    Water flux limit [m s-1]
    
    """

    # First, test if all water can simply be transferred into the lower subsurface layer:
    q_lim = GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx)

    # Calculate midpoint-to-midpoint distance between layers:
    dz = (GRID.get_node_height(Idx) + GRID.get_node_height(Idx + 1)) / 2

    # Calculate updated volumetric liquid water content:
    lwc_1 = GRID.get_node_liquid_water_content(Idx) - q_lim / GRID.get_node_height(Idx)
    lwc_2 = GRID.get_node_liquid_water_content(Idx + 1) + q_lim / GRID.get_node_height(Idx + 1)

    # Effective water saturation:
    theta_1 = effective_water_saturation(GRID, lwc_1, Idx)
    theta_2 = effective_water_saturation(GRID, lwc_2, Idx)

    # Hydraulic head:
    h_1 = hydraulic_head(GRID, theta_1, Idx)
    h_2 = hydraulic_head(GRID, theta_2, Idx + 1)

    # Evaluate if Hirashima et al. (2010) Eq. (20) is in equilibrium:
    residual = h_1 - (h_2 + dz)
    # If residual < 0 () & h_1 < h_2 --> Equilibrium cannot be attained, therefore all available water (q_lim) is transferred.
    # If residual > 0 () & h_1 > h_2 --> The iterative bi-section convergence algorithm below is executed to find the equilibrium point.

    if residual > 0:

        # Initial guess (half of the available water in the upper layer)
        q_lim = (GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx)) / 2

        # Establish iteration lower & upper bounds:
        q_lim_LB = 0                                                                    # q_lim Lower Bound (LB) 
        q_lim_UB = GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx)  # q_lim Upper Bound (UB)

        while abs(residual) > 1e-6:

            # Calculate updated volumetric liquid water content:
            lwc_1 = GRID.get_node_liquid_water_content(Idx) - q_lim / GRID.get_node_height(Idx)
            lwc_2 = GRID.get_node_liquid_water_content(Idx + 1) + q_lim / GRID.get_node_height(Idx + 1)

            # Effective water saturation:
            theta_1 = effective_water_saturation(GRID, lwc_1, Idx)
            theta_2 = effective_water_saturation(GRID, lwc_2, Idx)

            # Hydraulic head:
            h_1 = hydraulic_head(GRID, theta_1, Idx)
            h_2 = hydraulic_head(GRID, theta_2, Idx + 1)

            # Evaluate if Hirashima et al. (2010) Eq. (20) is in equilibrium:
            residual = h_1 - (h_2 + dz)
            if residual > 0:
                q_lim_UB = q_lim  # Excessive water transferred --> Curent q_lim becomes the new Upper Bound (UB)
            else:
                q_lim_LB = q_lim  # Insufficient water transferred --> Curent q_lim becomes the new Lower Bound (LB)

            # Next guess is the midpoint between the updated bounds / interval points:
            q_lim = (q_lim_UB + q_lim_LB) / 2

    return q_lim

    # Note: this iterative solver uses a basic, robust bisection algorithm but maybe faster by implementing a Newton-Raphson approach!

# ====================================================================================================================

# ================== #
# Hydraulic Head (h)
# ================== #

@njit
def hydraulic_head(GRID, theta, Idx):
    """ Calculates the hydraulic suction head (h) for a single subsurface layer
        according to Hirashima et al., (2010) (https://doi.org/10.1016/j.coldregions.2010.09.003) - Eqs. (9) & (17)

        Input:
                    GRID     ::    Subsurface GRID variables -->
                    d        ::    Layer grain size [mm]
                    theta    ::    Layer saturation [-]
        Output:
                    h        ::    Layer hydaulic head [m]
    """

    n = 15.68 * np.exp(-0.46 * GRID.get_node_grain_size(Idx)) + 1
    m = 1 - 1 / n
    return 1 / (7.3 * np.exp(1.9)) * (max(theta, 1e-12) ** (-1 / m) - 1) ** (1 / n)

# ====================================================================================================================

# ============================== #
# Effective Water Saturation (Θ)
# ============================== #

@njit
def effective_water_saturation(GRID, lwc, Idx):
    """ Calculates the effective water saturation (Θ) for a single subsurface layer
        according to Hirashima et al., (2010) (https://doi.org/10.1016/j.coldregions.2010.09.003) - Eq. (5)
        and Yamaguchi et al., (2010) (https://doi.ord/10.1016/j.coldregions.2010.05.008) - residual water content

        Parameters:
                    snow_ice_threshold    ::    Pore close density [kg m-3]

        Input:
                    GRID     ::    Subsurface GRID variables -->
                    lwc      ::    Layer liquid water content [-] 
                    irr      ::    Layer irreducible water content [-]
                    icf      ::    Layer ice fraction [-]

        Output:
                    theta    ::    Layer saturation [-]

"""
    return min(1,max(0,((lwc - GRID.get_node_irreducible_water_content(Idx)) / \
              (((snow_ice_threshold - GRID.get_node_ice_fraction(Idx) * ice_density) / water_density) - GRID.get_node_irreducible_water_content(Idx)))))

# ====================================================================================================================