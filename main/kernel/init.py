
"""
    ==================================================================

                          INITIALISATION (INIT) FILE

        This file initialises the model's subsurface grid (snowpack) 
        according to the user-specified initial conditions in the 
        parameters file.

    ==================================================================
"""

import numpy as np
import math as mt
from constants import *
from config import *
from main.kernel.grid import *

# =================== #
# Initialise Snowpack
# =================== #

def init_snowpack(STATIC):
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

    # Override initial glacier & snow heights if glacier thickness provided in the static file
    if 'THICKNESS' in list(STATIC.keys()):
        snowheight = min(STATIC.THICKNESS.values, initial_snowheight)
        glacier_height = max(STATIC.THICKNESS.values - initial_snowheight, 0)
    else:
        snowheight = initial_snowheight
        glacier_height = initial_glacier_height

    # Base elevation:
    base_elevation = STATIC.ELEVATION.values - (snowheight + glacier_height)

    # =================== #
    # Snowpack & Glacier:
    # =================== #    

    # Snow / firn layers     
    if (snowheight > 0.0):

        if snowheight < coarse_layer_threshold:

            # Calculate the number of full snow layers:
            n_full_layers = mt.floor(snowheight / initial_snow_layer_heights)

            # Surface layer height
            surface_layer_height = snowheight % initial_snow_layer_heights
            if surface_layer_height < minimum_snow_layer_height:
                layer_heights = np.ones(n_full_layers) * initial_snow_layer_heights
                layer_heights[0] = layer_heights[0] + surface_layer_height
            else:
                layer_heights = np.concatenate((np.array([surface_layer_height]), (np.ones(n_full_layers) * initial_snow_layer_heights)))
        
            # Number of snow layers
            n_snow_layers = len(layer_heights)

        else:

            # Calculate the number of full fine snow layers: 
            n_full_fine_layers = mt.floor(coarse_layer_threshold / initial_snow_layer_heights)
            fine_layer_heights = np.ones(n_full_fine_layers) * initial_snow_layer_heights

            # Calculate the number of full coarse snow layers:
            n_full_coarse_layers = mt.floor((snowheight - coarse_layer_threshold) / maximum_coarse_layer_height)
            coarse_layer_heights = np.ones(n_full_coarse_layers) * maximum_coarse_layer_height

            # Surface layer height
            surface_layer_height = snowheight - (np.sum(fine_layer_heights) + np.sum(coarse_layer_heights))
            if surface_layer_height < minimum_snow_layer_height:
                layer_heights = np.concatenate((fine_layer_heights, coarse_layer_heights))
                layer_heights[0] = layer_heights[0] + surface_layer_height
            else:
                layer_heights = np.concatenate((np.array([surface_layer_height]), fine_layer_heights, coarse_layer_heights))

            # Number of snow layers
            n_snow_layers = len(layer_heights)

        # Calculate midpoint depth of layers
        midpoint_depths = np.cumsum(layer_heights) - (layer_heights / 2.0)
        
        # Calculate temperature and density gradients
        dT = ((initial_upper_temperature + zero_temperature) - (initial_lower_temperature + zero_temperature)) / (snowheight + glacier_height)
        drho = (initial_upper_snowpack_density - initial_lower_snowpack_density) / snowheight

        # Initialise snow layer variables
        layer_densities = initial_upper_snowpack_density - (drho * midpoint_depths)
        layer_T = (initial_upper_temperature + zero_temperature) - (dT * midpoint_depths)
        layer_liquid_water = np.zeros(n_snow_layers)
        layer_refreeze = np.zeros(n_snow_layers)
        layer_firn_refreeze = np.zeros(n_snow_layers)
        layer_hydro_year = np.zeros(n_snow_layers)
        layer_grain_size = initial_snow_grain_size + (layer_densities / snow_ice_threshold) * (initial_ice_grain_size - initial_snow_grain_size)

        # Number of glacier layers
        n_glacier_layers = int(glacier_height / initial_glacier_layer_heights)

        # Glacier layer heights:
        glacier_layer_heights = np.ones(n_glacier_layers) * initial_glacier_layer_heights

        # Calculate midpoint depth of layers
        midpoint_depths = (np.cumsum(glacier_layer_heights) - (glacier_layer_heights / 2.0)) + np.sum(layer_heights)

        # Initialise full glacier layer variables
        layer_T = np.concatenate((layer_T, (initial_upper_temperature + zero_temperature) - (dT * midpoint_depths)))
        layer_heights = np.concatenate((layer_heights, np.ones(n_glacier_layers) * initial_glacier_layer_heights))
        layer_densities = np.concatenate((layer_densities, np.ones(n_glacier_layers) * ice_density))
        layer_liquid_water = np.concatenate((layer_liquid_water, np.zeros(n_glacier_layers)))
        layer_refreeze = np.concatenate((layer_refreeze, np.zeros(n_glacier_layers)))
        layer_firn_refreeze = np.concatenate((layer_firn_refreeze, np.zeros(n_glacier_layers)))
        layer_hydro_year = np.concatenate((layer_hydro_year, np.zeros(n_glacier_layers)))
        layer_grain_size = np.concatenate((layer_grain_size, np.full(n_glacier_layers, initial_ice_grain_size)))
    
    # ============= #
    # Glacier only:
    # ============= #

    else:

        # Number of glacier layers
        n_glacier_layers = int(glacier_height / initial_glacier_layer_heights)

        # Glacier layer heights:
        glacier_layer_heights = np.ones(n_glacier_layers) * initial_glacier_layer_heights        

        # Calculate midpoint depth of layers
        midpoint_depths = np.cumsum(glacier_layer_heights) - (glacier_layer_heights / 2.0)

        # Calculate temperature gradient
        dT = ((initial_upper_temperature + zero_temperature) - (initial_lower_temperature + zero_temperature)) / glacier_height

        # Initialise glacier layer variables
        layer_heights = np.ones(n_glacier_layers) * initial_glacier_layer_heights
        layer_densities = np.ones(n_glacier_layers) * ice_density
        layer_T = (initial_upper_temperature + zero_temperature) - (dT * midpoint_depths)
        layer_liquid_water = np.zeros(n_glacier_layers)
        layer_refreeze = np.zeros(n_glacier_layers)
        layer_firn_refreeze = np.zeros(n_glacier_layers)
        layer_hydro_year = np.zeros(n_glacier_layers)
        layer_grain_size = np.full(n_glacier_layers, initial_ice_grain_size)

    # ================ #
    # Initialise GRID:
    # ================ #

    GRID = Grid(layer_heights.astype(np.float64), 
                layer_densities.astype(np.float64), 
                layer_T.astype(np.float64),
                layer_T.astype(np.float64).copy(), 
                layer_liquid_water.astype(np.float64), 
                layer_refreeze.astype(np.float64), 
                layer_firn_refreeze.astype(np.float64), 
                layer_hydro_year.astype(np.int32), 
                layer_grain_size.astype(np.float64),
                float(base_elevation),
                None,   # layer_ice_fraction
                None,   # new_snow_height
                None,   # new_snow_timestamp
                None,   # old_snow_timestamp
                None)   # fresh_snow_timestamp
    
    return GRID

# ==================================================================================================================== #