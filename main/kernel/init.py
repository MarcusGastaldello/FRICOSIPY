
"""
    ==================================================================

                          INITIALISATION (INIT) FILE

        This file initialises the model's subsurface grid (snowpack) 
        according to the user-specified initial conditions in the 
        parameters file.

    ==================================================================
"""

import numpy as np
from constants import *
from config import *
from main.kernel.grid import *

# =================== #
# Initialise Snowpack
# =================== #

def init_snowpack():
    """ This function initialises the snowpack / glacier for the first simulation time step """
	
    # Initialise layer variable arrays
    layer_heights = []
    layer_densities = []
    layer_T = []
    layer_liquid_water = []
    layer_refreeze = []
    layer_firn_refreeze = []
    layer_hydro_year = []
    layer_grain_size = []

    # =================== #
    # Snowpack & Glacier:
    # =================== #    

    # Snow / firn layers     
    if (initial_snowheight > 0.0):
        nlayers = int(initial_snowheight / initial_snow_layer_heights)
        dT = (initial_upper_temperature - initial_lower_temperature) / (initial_snowheight + initial_glacier_height)
        if nlayers == 0:
            layer_heights = np.array([initial_snowheight])
            layer_densities = np.array([initial_upper_snowpack_density])
            layer_T = np.array([initial_upper_temperature])
            layer_liquid_water = np.array([0.0])
            layer_refreeze = np.array([0.0])
            layer_firn_refreeze = np.array([0.0])
            layer_hydro_year = np.array([0.0])
            layer_grain_size = np.array([initial_snow_grain_size])
        elif nlayers > 0:
            drho = (initial_upper_snowpack_density - initial_lower_snowpack_density) / initial_snowheight
            layer_heights = np.ones(nlayers) * (initial_snowheight / nlayers)
            layer_densities = np.array([initial_upper_snowpack_density - drho * (initial_snowheight / nlayers) * i for i in range(1, nlayers + 1)])
            layer_T = np.array([initial_upper_temperature - dT * (initial_snowheight / nlayers) * i for i in range(1, nlayers + 1)])
            layer_liquid_water = np.zeros(nlayers)
            layer_refreeze = np.zeros(nlayers)
            layer_firn_refreeze = np.zeros(nlayers)
            layer_hydro_year = np.zeros(nlayers)
            layer_grain_size = initial_snow_grain_size + (layer_densities / snow_ice_threshold) * (initial_ice_grain_size - initial_snow_grain_size)

        # Glacier layers
        nlayers = int(initial_glacier_height / initial_glacier_layer_heights)
        layer_heights = np.append(layer_heights, np.ones(nlayers) * initial_glacier_layer_heights)
        layer_densities = np.append(layer_densities, np.ones(nlayers)*ice_density)
        layer_T = np.append(layer_T, [layer_T[-1] - dT * initial_glacier_layer_heights * i for i in range(1, nlayers + 1)])
        layer_liquid_water = np.append(layer_liquid_water, np.zeros(nlayers))
        layer_refreeze = np.append(layer_refreeze, np.zeros(nlayers))
        layer_firn_refreeze = np.append(layer_firn_refreeze, np.zeros(nlayers))
        layer_hydro_year = np.append(layer_hydro_year, np.zeros(nlayers))
        layer_grain_size = np.append(layer_grain_size, np.full(nlayers, initial_ice_grain_size))
    
    # ============= #
    # Glacier only:
    # ============= #

    else:
        nlayers = int(initial_glacier_height / initial_glacier_layer_heights)
        dT = (initial_upper_temperature - initial_lower_temperature) / initial_glacier_height
        layer_heights = np.ones(nlayers) * initial_glacier_layer_heights
        layer_densities = np.ones(nlayers) * ice_density
        layer_T = np.array([initial_upper_temperature - dT * initial_glacier_layer_heights * i for i in range(1, nlayers + 1)])
        layer_liquid_water = np.zeros(nlayers)
        layer_refreeze = np.zeros(nlayers)
        layer_firn_refreeze = np.zeros(nlayers)
        layer_hydro_year = np.zeros(nlayers)
        layer_grain_size = np.full(nlayers, initial_ice_grain_size)

    # ================ #
    # Initialise GRID:
    # ================ #

    GRID = Grid(np.array(layer_heights, dtype = np.float64), 
                np.array(layer_densities, dtype = np.float64), 
                np.array(layer_T, dtype = np.float64), 
                np.array(layer_liquid_water, dtype = np.float64), 
                np.array(layer_refreeze, dtype = np.float64), 
                np.array(layer_firn_refreeze, dtype = np.float64), 
                np.array(layer_hydro_year, dtype = 'int32'), 
                np.array(layer_grain_size, dtype = np.float64), 
                None, 
                None, 
                None, 
                None, 
                None)
    
    return GRID

# ==================================================================================================================== #