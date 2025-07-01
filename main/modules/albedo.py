import numpy as np
from constants import *
from parameters import *
from numba import njit

@njit
def update_albedo(GRID,albedo_snow,surface_temperature):
    """ This methods updates the albedo """
    albedo_allowed = ['Oerlemans98','Bougamont05','measured']
    if albedo_method == 'Oerlemans98':
        albedo, albedo_snow = method_Oerlemans(GRID)
    elif albedo_method == 'Bougamont05':
        albedo, albedo_snow = method_Bougamont(GRID,albedo_snow,surface_temperature)
    else:
        raise ValueError("Albedo method = \"{:s}\" is not allowed, must be one of {:s}".format(albedo_method, ", ".join(albedo_allowed)))

    return albedo, albedo_snow

# ====================================================================================================================

@njit
def method_Oerlemans(GRID):
    """Albedo decay is calculated based on the parameterisation of Oerlemans and Knapp (1998)"""

    # Get hours since the last snowfall
    # First get fresh snow properties (height and timestamp)
    fresh_snow_height, fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()
    
    # Get time difference between last snowfall and now
    hours_since_snowfall = (fresh_snow_timestamp)/3600.0

    # If fresh snow disappears faster than the snow ageing scale then set the hours_since_snowfall
    # to the old values of the underlying snowpack
    if (hours_since_snowfall<(albedo_mod_snow_aging*24)) & (fresh_snow_height<0.0):
        GRID.set_fresh_snow_props_to_old_props()
        fresh_snow_height, fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()
        
        # Update time difference between last snowfall and now
        hours_since_snowfall = (fresh_snow_timestamp)/3600.0

    # Check if snow or ice
    if (GRID.get_node_density(0) <= snow_ice_threshold):
        
        # Get current snowheight from layer height
        h = GRID.get_total_snowheight() #np.sum(GRID.get_height()[0:idx])

        # Surface albedo according to Oerlemans & Knap 1998, JGR)
        alphaSnow = albedo_firn + (albedo_fresh_snow - albedo_firn) *  np.exp((-hours_since_snowfall) / (albedo_mod_snow_aging * 24.0))
        albedo = alphaSnow + (albedo_ice - alphaSnow) *  np.exp((-1.0*h) / (albedo_mod_snow_depth / 100.0))

    else:
        # If no snow cover than set albedo to ice albedo
        albedo = albedo_ice

    # Snow albedo
    albedo_snow = None

    return albedo, albedo_snow

# ====================================================================================================================

@njit
def method_Bougamont(GRID,albedo_snow,surface_temperature):
    """Albedo decay is calculated based on the parameterisation of Bougamont et al. (2005)"""

    # Get hours since the last snowfall
    # First get fresh snow properties (height and timestamp)
    _ , fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()

    # Get time difference between last snowfall and now:
    hours_since_snowfall = (fresh_snow_timestamp) / 3600.0

    # Convert integration time from seconds to days
    dt_days = dt / 86400.0

    # Get current snowheight from layer height
    h = GRID.get_total_snowheight()

    # Check if snow or ice
    if (GRID.get_node_density(0) <= snow_ice_threshold):

        # Calculate albedo decay coefficient:
        if surface_temperature >= zero_temperature:
            t_star = t_star_wet
        else:
            if surface_temperature < t_star_cutoff:
                t_star = t_star_dry + (273.15 - t_star_cutoff) * t_star_K
            else:
                t_star = t_star_dry + (273.15 - surface_temperature) * t_star_K

        # Effect of snow albedo decay due to the temporal metamorphosis of snow:
        albedo_snow = albedo_snow - (albedo_snow - albedo_firn) / t_star * dt_days

        # Reset if snowfall in current timestep
        if hours_since_snowfall == 0:    
            albedo_snow = albedo_fresh_snow

        # Effect of surface albedo decay due to the snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * h) / (albedo_mod_snow_depth / 100.0))

    else:
        albedo = albedo_ice

    albedo = float(albedo)

    return albedo, albedo_snow

# ====================================================================================================================

