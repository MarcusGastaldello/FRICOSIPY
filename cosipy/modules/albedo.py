import numpy as np
from constants import *
from parameters import *

# ============== #
# Surface Albedo
# ============== #

def update_albedo(GRID,albedo_snow,surface_temperature):
    """ This methods updates the albedo """
    albedo_allowed = ['Oerlemans98','Bougamont05']

    # Get hours since the last snowfall
    # First get fresh snow properties (height and timestamp)
    _ , fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()

    # Convert integration time from seconds to days
    dt_days = dt / 86400.0

    # Check if snow or ice
    if (GRID.get_node_density(0) <= snow_ice_threshold):

        # Albedo decay method
        if albedo_method == 'Oerlemans98':
            t_star = method_Oerlemans()
        elif albedo_method == 'Bougamont05':
            t_star = method_Bougamont(surface_temperature)
        else:
            raise ValueError("Albedo method = \"{:s}\" is not allowed, must be one of {:s}".format(albedo_method, ", ".join(albedo_allowed)))     

        # Effect of snow albedo decay due to the temporal metamorphosis of snow:
        albedo_snow = albedo_snow - (albedo_snow - albedo_firn) / t_star * dt_days 

        # Effect of surface albedo decay due to the snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * GRID.get_total_snowheight()) / (albedo_mod_snow_depth / 100.0))

        # Reset if snowfall in current timestep
        if fresh_snow_timestamp == 0:    
            albedo = albedo_fresh_snow

    else:
        albedo = albedo_ice

    return albedo, albedo_snow

# ====================================================================================================================

# ============================= #
# Oerlemans & Knapp 1998 Method
# ============================= #

def method_Oerlemans():
    """Albedo decay is calculated based on the parameterisation of Oerlemans and Knapp (1998)"""

    t_star = albedo_mod_snow_aging

    return t_star

# ====================================================================================================================

# ================================== #
# Bougamont et al., 2005 Enhancememt
# ================================== #

def method_Bougamont(surface_temperature):
    """Albedo decay is calculated based on the enhancement of Oerlemans and Knapp (1998) by Bougamont et al. (2005)"""
    
    # Calculate albedo temporald decay coefficient:
    if surface_temperature >= zero_temperature:
        t_star = t_star_wet
    else:
        if surface_temperature < t_star_cutoff:
            t_star = t_star_dry + (273.15 - t_star_cutoff) * t_star_K
        else:
            t_star = t_star_dry + (273.15 - surface_temperature) * t_star_K

    return t_star

# ====================================================================================================================