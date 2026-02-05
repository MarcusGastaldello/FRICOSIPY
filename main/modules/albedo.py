"""
    ==================================================================

                            SURFACE ALBEDO MODULE

        This module calculates the temporal decay of the surface 
        albedo during a single model timestep.

    ==================================================================
"""

import numpy as np
from constants import *
from parameters import *
from numba import njit

def update_albedo(GRID,albedo_snow,surface_temperature):
    """ This function calculates the temporal change of the surface albedo """

    albedo_allowed = ['Oerlemans98','Bougamont05']
    if albedo_method == 'Oerlemans98':
        albedo, albedo_snow = method_Oerlemans(GRID)
    elif albedo_method == 'Bougamont05':
        albedo, albedo_snow = method_Bougamont(GRID,albedo_snow,surface_temperature)
    else:
        raise ValueError("Albedo method = \"{:s}\" is not allowed, must be one of {:s}".format(albedo_method, ", ".join(albedo_allowed)))

    return albedo, albedo_snow

# ====================================================================================================================

# ============================= #
# Oerlemans & Knapp 1998 Method
# ============================= #

@njit
def method_Oerlemans(GRID):
    """ Albedo is calculated as an exponentially decreasing function of time since the last significant snowfall event
        after Oerlemans and Knapp (1998)

        Parameters:
                    albedo_fresh_snow                   ::    Fresh snow albedo [-]
                    albedo_firn                         ::    Firn albedo [-]
                    albedo_ice                          ::    Ice albedo [-]
                    albedo_decay_timescale              ::    Albedo decay timescale [days]
                    albedo_characteristic_snow_depth    ::    Albedo characteristic scale for snow depth [cm]
        Input: 
                    GRID                                ::    Subsurface GRID variables

        Output:
                    albedo_snow                         ::    Snow surface albedo [-]
                    albedo                              ::    Surface albedo (adjusted for snow depth) [-]
           
    """

    # Get hours since the last snowfall
    # First get fresh snow properties (height and timestamp)
    fresh_snow_height, fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()
    
    # Get time difference between last snowfall and now
    hours_since_snowfall = (fresh_snow_timestamp) / 3600.0

    # If fresh snow disappears faster than the snow ageing scale then set the hours_since_snowfall
    # to the old values of the underlying snowpack
    if (hours_since_snowfall < ( albedo_decay_timescale * 24)) & (fresh_snow_height < 0.0):
        GRID.set_fresh_snow_props_to_old_props()
        fresh_snow_height, fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()
        
        # Update time difference between last snowfall and now
        hours_since_snowfall = (fresh_snow_timestamp) / 3600.0

    # Check if snow or ice
    if (GRID.get_node_density(0) < snow_ice_threshold):
        
        # Get current snowheight from layer height
        h = GRID.get_total_snowheight() 

        # Surface albedo according to Oerlemans & Knap 1998, JGR)
        albedo_snow = albedo_firn + (albedo_fresh_snow - albedo_firn) *  np.exp((-hours_since_snowfall) / (albedo_decay_timescale * 24.0))

        # Adjustment of surface albedo for snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * h) / (albedo_characteristic_snow_depth / 100.0))

    else:
        # If no snow cover than set albedo to ice albedo
        albedo = albedo_ice

    return albedo, albedo_snow

# ====================================================================================================================

# ===================== #
# Bougamont 2005 Method
# ===================== #

@njit
def method_Bougamont(GRID,albedo_snow,surface_temperature):
    """ Albedo is calculated as an exponentially decreasing function of time since the last significant snowfall event
        with a surface temperature dependant decay timescale.
        after Oerlemans and Knapp (1998) (modified by Bougamont et al. (2005)) 
        
        Parameters:
                    albedo_snow                              ::    Fresh snow albedo [-]
                    albedo_firn                              ::    Firn albedo [-]
                    albedo_ice                               ::    Ice albedo [-]
                    albedo_decay_timescale_dry               ::    Decay timescale (dry snow surface at 0 °C) [days]
                    albedo_decay_timescale_wet               ::    Decay timescale (melting surface) [days]
                    albedo_decay_timescale_dry_adjustment    ::    Increase in decay timescale at negative temperatures [day K-1]
                    albedo_decay_timescale_threshold         ::    Temperature threshold for decay timescale increase [K]
                    albedo_characteristic_snow_depth         ::    Albedo snow depth adjustment parameter [cm]
        Input: 
                    GRID                                     ::    Subsurface GRID variables
                    albedo snow                              ::    Snow surface albedo [-]
                    surface_temperature                      ::    Surface temperature [K]

        Output:
                    albedo_snow                              ::    Snow surface albedo [-]
                    albedo                                   ::    Surface albedo (adjusted for snow depth) [-]
        
    """

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
            albedo_decay_timescale_bougamont = albedo_decay_timescale_wet
        else:
            if surface_temperature < albedo_decay_timescale_threshold:
                albedo_decay_timescale_bougamont = albedo_decay_timescale_dry + (zero_temperature - albedo_decay_timescale_threshold) * albedo_decay_timescale_dry_adjustment
            else:
                albedo_decay_timescale_bougamont = albedo_decay_timescale_dry + (zero_temperature - surface_temperature) * albedo_decay_timescale_dry_adjustment

        # Effect of snow albedo decay due to the temporal metamorphosis of snow:
        albedo_snow = albedo_snow - (albedo_snow - albedo_firn) / albedo_decay_timescale_bougamont * dt_days

        # Reset if snowfall in current timestep
        if hours_since_snowfall == 0:    
            albedo_snow = albedo_fresh_snow

        # Adjustment of surface albedo for snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * h) / (albedo_characteristic_snow_depth / 100.0))

    else:
        albedo = albedo_ice

    albedo = float(albedo)

    return albedo, albedo_snow

# ====================================================================================================================

