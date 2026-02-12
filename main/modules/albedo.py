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

def update_albedo(GRID, surface_temperature):
    """ This function calculates the temporal change of the surface albedo """

    albedo_allowed = ['Oerlemans98','Bougamont05']
    if albedo_method == 'Oerlemans98':
        albedo = method_Oerlemans(GRID)
    elif albedo_method == 'Bougamont05':
        albedo = method_Bougamont(GRID, surface_temperature)
    else:
        raise ValueError("Albedo method = \"{:s}\" is not allowed, must be one of {:s}".format(albedo_method, ", ".join(albedo_allowed)))

    return albedo

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
                    GRID                                ::    Subsurface GRID variables -->

        Output:
                    albedo                              ::    Surface albedo (adjusted for snow depth) [-]
           
    """

    # Get fresh snow properties
    snow_age, _ , _   = GRID.get_fresh_snow_props()
    
    # Get hours since last snowfall
    hours_since_snowfall = snow_age / 3600.0

    # Get current snowheight from layer heights
    h = GRID.get_total_snowheight() 

    # Check if snow or ice
    if (GRID.get_node_density(0) < snow_ice_threshold):

        # Surface albedo according to Oerlemans & Knap 1998, JGR)
        albedo_snow = albedo_firn + (albedo_fresh_snow - albedo_firn) *  np.exp((-hours_since_snowfall) / (albedo_decay_timescale * 24.0))

        # Reset if snowfall in current timestep
        if snow_age == 0:    
            albedo_snow = albedo_fresh_snow

        # Updates the fresh snow albedo property
        GRID.set_fresh_snow_albedo(albedo_snow)

        # Adjustment of surface albedo for snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * h) / (albedo_characteristic_snow_depth / 100.0))

    else:
        # If no snow cover than set albedo to ice albedo
        albedo = albedo_ice

    return albedo

# ====================================================================================================================

# ===================== #
# Bougamont 2005 Method
# ===================== #

@njit
def method_Bougamont(GRID,surface_temperature):
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
                    albedo_decay_timescale_threshold         ::    Temperature threshold for decay timescale increase [°C]
                    albedo_characteristic_snow_depth         ::    Albedo snow depth adjustment parameter [cm]
        Input: 
                    GRID                                     ::    Subsurface GRID variables -->
                    albedo snow                              ::    Snow surface albedo [-]
                    surface_temperature                      ::    Surface temperature [K]

        Output:
                    albedo                                   ::    Surface albedo (adjusted for snow depth) [-]
        
    """

    # Get fresh snow properties
    snow_age, albedo_snow , _  = GRID.get_fresh_snow_props()

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
            if surface_temperature < (albedo_decay_timescale_threshold + zero_temperature):
                albedo_decay_timescale_bougamont = albedo_decay_timescale_dry - albedo_decay_timescale_threshold * albedo_decay_timescale_dry_adjustment
            else:
                albedo_decay_timescale_bougamont = albedo_decay_timescale_dry + (zero_temperature - surface_temperature) * albedo_decay_timescale_dry_adjustment

        # Effect of snow albedo decay due to the temporal metamorphosis of snow:
        albedo_snow = albedo_snow - (albedo_snow - albedo_firn) / albedo_decay_timescale_bougamont * dt_days
        albedo_snow = max(min(albedo_fresh_snow, albedo_snow), albedo_firn)

        # Reset if snowfall in current timestep
        if snow_age == 0:    
            albedo_snow = albedo_fresh_snow

        # Updates the fresh snow albedo property
        GRID.set_fresh_snow_albedo(albedo_snow)

        # Adjustment of surface albedo for snow depth:
        albedo = albedo_snow + (albedo_ice - albedo_snow) *  np.exp((-1.0 * h) / (albedo_characteristic_snow_depth / 100.0))

    else:
        albedo = albedo_ice

    albedo = float(albedo)

    return albedo

# ====================================================================================================================

