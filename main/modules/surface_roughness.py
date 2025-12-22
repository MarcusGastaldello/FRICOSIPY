"""
    ==================================================================

                          SURFACE ROUGHNESS MODULE

        This module determines the temporal change of the 
        surface roughness for a single model timestep.

    ==================================================================
"""

from constants import *
from parameters import *

# ================= #
# Surface Roughness
# ================= #

def update_roughness(GRID):
    """ This module calculates the temporal change of the surface roughess """
    
    surface_roughness_allowed = ['Moelg12','constant']
    if surface_roughness_method == 'Moelg12':
        surface_roughness = method_Moelg(GRID)
    elif surface_roughness_method == 'constant':
        surface_roughness = constant_surface_roughness
    else:
        raise ValueError("Surface roughness method = \"{:s}\" is not allowed, must be one of {:s}".format(surface_roughness_method,", ".join(surface_roughness_allowed)))
    return surface_roughness

# ====================================================================================================================

# ========================= #
# Moelg et al., 2012 Method
# ========================= #

def method_Moelg(GRID):
    """ Surface roughness is calculated as a linearly increasing function of time since the last significant snowfall event
        after Moelg et al. (2012)

        Parameters:
                    surface_roughness_fresh_snow      ::    Surface roughness of fresh snow [mm]
                    surface_roughness_firn            ::    Surface roughness of firn [mm] 
                    surface_roughness_ice             ::    Surface roughness of ice [mm]
                    surface_roughness_timescale       ::    Surface roughness linear timescale [mm h-1] 
        Input:
                    GRID                              ::    Subsurface GRID variables
        Output:  
                    surface_roughness                 ::    Surface roughness (updated) [m]
    """

    # Get hours since the last snowfall
    # First get fresh snow properties (height and timestamp)
    _ , fresh_snow_timestamp, _  = GRID.get_fresh_snow_props()

    # Get time difference between last snowfall and now
    hours_since_snowfall = (fresh_snow_timestamp) / 3600.0

    # Check whether snow or ice
    if (GRID.get_node_density(0) <= snow_ice_threshold):

        # Roughness length linearly increases based on the surface roughness timescale 
        surface_roughness = min(surface_roughness_fresh_snow + surface_roughness_timescale * hours_since_snowfall, surface_roughness_firn)

    else:

        # Roughness length, set to ice
        surface_roughness = surface_roughness_ice

    # Convert from mm to m:
    surface_roughness = surface_roughness / 1000

    return surface_roughness

# ====================================================================================================================
