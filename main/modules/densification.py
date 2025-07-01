import numpy as np
from constants import *
from parameters import *
from numba import njit

# ================= #
# Dry Densification
# ================= #

@njit
def densification(GRID,ACCUMULATION,dt):
    """ Densification of the snowpack
    Args:
        GRID    ::  GRID-Structure
	dt      ::  integration time
    """

    densification_allowed = ['Boone', 'Ligtenberg11', 'constant']
    if densification_method == 'Boone':
        method_Boone(GRID,dt)
    elif densification_method == 'Ligtenberg11':
        method_Ligtenberg(GRID,ACCUMULATION,dt)
    elif densification_method == 'constant':
        pass
    else:
        raise ValueError("Densification method = \"{:s}\" is not allowed, must be one of {:s}".format(densification_method, ", ".join(densification_allowed)))

# ====================================================================================================================

# ================= #
# Boone 2002 Method
# ================= #

@njit
def method_Boone(GRID,dt):
    """ Description: Densification through overburden pressure
        after Essery et al. 2013
    """

    # Constants
    # Snow Settling Parameters
    c1 = 2.8e-6 # 2.8x10-6 s-1 (Anderson 1976) 
    c2 = 0.042 # 4.2x10-2 K-1 (Anderson 1976)
    c3 = 0.046 # 460 m3 kg-1 (Anderson 1976) (COSIPY and Essery 2013 0.046)
    rho0 = 150 # 150 kg m-3 (Anderson 1976)
    # Snow Viscosity Parameters
    c4 = 0.081 # 8.1x10-2 K-1 (Boone 2002 | Kojima 1967 | Mellor 1964) 
    c5 = 0.018 # 1.8x10-2 m3 kg-1 (Boone 2002 | Kojima 1967 | Mellor 1964)
    # Snow Viscosity Coefficient 
    eta0 = 3.7e7 # 3.7x10+7 Pa s (Boone 2002 | Kojima 1967 | Mellor 1964)

    rho = np.array(GRID.get_density())
    h   = np.array(GRID.get_height())
    T   = np.array(GRID.get_temperature())
    theta_ice = np.array(GRID.get_ice_fraction())

    # Overburden nodal snow mass (subtract half of layer height to get nodal centre):
    M_s = np.cumsum(rho * h) - (0.5 * h * rho)

    # Viscosity
    eta = eta0 * np.exp(c4 * (zero_temperature - T) + c5 * rho) # checked

    # Binary mask for snow/ice determination:
    mask = np.where(rho < snow_ice_threshold,1,0)

    # Layer density change:
    drho = mask * (((M_s * 9.81) / eta) + c1 * np.exp(-c2 * (zero_temperature - T) - c3 * np.maximum(0.0, rho - rho0))) * dt * rho

    # Calculate change in volumetric ice fraction:
    dtheta_i = drho / ice_density

    # Set updated volumetric ice fraction:
    GRID.set_ice_fraction(dtheta_i + theta_ice)

    # Set updated layer height due to compaction:
    GRID.set_height(np.maximum(minimum_snow_layer_height, h * (rho / (rho + drho))))

# ====================================================================================================================

# ================================================================= #
# Arthern et al., 2010 (modified by Ligtenberg et al., 2011) Method
# ================================================================= #

@njit
def method_Ligtenberg(GRID,ACCUMULATION,dt):
    """ Description: Densification based on in situ measurements of Antarctic snow compaction (used in the EBFM)
        after Arthern et al. 2010 (modified by Ligtenberg et al. 2011)
    """

    # Constants
    g = 9.81 # gravitational acceleration [m s-2]
    R = 8.314 # universal gas constant [J mol-1]
    Ec = 60e3 # creep by lattice diffusion activation energy [J mol-1]
    Eg = 42.4e3 # grain growth activation energy [J mol-1]

    # Extract variables:
    rho = np.asarray(GRID.get_density())
    h   = np.asarray(GRID.get_height())
    T   = np.asarray(GRID.get_temperature())
    theta_ice = np.asarray(GRID.get_ice_fraction())
    z   = np.asarray(GRID.get_depth())

    # Convert units:
    b = ACCUMULATION * 1000 # accumulation [mm a-1]
    dt = dt / 31536000 # timestep as a fraction of a calendar year

    # Binary mask for snow/ice determination:
    mask = np.where(rho < snow_ice_threshold,1,0)

    # Gravitational Constant:
    C_snow = 0.07 * np.maximum(1.435 - 0.151 * np.log(b) , 0.25)
    C_firn = 0.03 * np.maximum(2.366 - 0.293 * np.log(b) , 0.25)
    C = np.where(rho < 550, C_snow , C_firn)

    # Obtain approximate temperatures from interpolation depths z1 & z2
    Tz1 = T[np.searchsorted(z, z1, side="left")]
    Tz2 = T[np.searchsorted(z, z2, side="left")]
    
    # Calculate linear temperature profile model constants
    m = (Tz2 - Tz1) / (z2 - z1)
    q = Tz1 - (m * z1)
    
    # Calculate approximate annual average temperature from linear gradient interpolation
    T_AVG = z * m + q
    
    # Layer density change:
    drho = mask * dt * C * b * g * (ice_density - rho) * np.exp((-Ec / (R * T)) + (Eg / (R * T_AVG)))

    # Calculate change in volumetric ice fraction:
    dtheta_i = drho / ice_density

    # Set updated volumetric ice fraction:
    GRID.set_ice_fraction(dtheta_i + theta_ice)

    # Set updated layer height due to compaction:
    GRID.set_height(h * (rho / (rho + drho)))

# ====================================================================================================================
