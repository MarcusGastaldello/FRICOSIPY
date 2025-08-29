"""
    ==================================================================

                          PENETRATING RADIATION MODULE

        This module calculates the amount of subsurface melting 
        from shortwave radiation bypassing the surface energy 
        balance and directly penetrating into the snowpack during 
        a single model timestep.

    ==================================================================
"""

import numpy as np
from constants import *
from parameters import *
from numba import njit

# ===================== #
# Penetrating Radiation
# ===================== #

@njit
def penetrating_radiation(GRID, SW_net, dt):
    """ This module calculates the amount of subsurface melt from penetrating shortwave radiation """
    penetrating_allowed = ['Bintanja95','disabled']
    if penetrating_method == 'Bintanja95':
        subsurface_melt, SW_penetrating = method_Bintanja(GRID, SW_net, dt)
    elif penetrating_method == 'disabled':
        subsurface_melt = 0.
        SW_penetrating = 0.
    else:
        raise ValueError("Penetrating method = \"{:s}\" is not allowed, must be one of {:s}".format(penetrating_method, ", ".join(penetrating_allowed)))

    return subsurface_melt, SW_penetrating

# ====================================================================================================================

# ===================================== #
# Bintanja & van den Broeke 1995 Method
# ===================================== #

@njit
def method_Bintanja(GRID, SW_net, dt):
    """ Shortwave radiation is apportioned to bypass the surface energy balance and directly melt subsurface layers
        based on Bintanja and van den Broeke (1995) 
        
        Parameters:
                    dt                       ::    Integration time in a model time-step [s]
                    extinction_coeff_snow    ::    Extinction coefficient for snow [m-1]
                    extinction_coeff_ice     ::    Extinction coefficient for ice [m-1]
        Input: 
                    GRID                     ::    Subsurface GRID variables -->
                    d (z)                    ::    Layer depth [m]
                    lwc (z)                  ::    Layer liquid water content [-] 
                    icf (z)                  ::    Layer ice fraction [-]
                    T (z)                    ::    Layer temperature [K]
                    c (z)                    ::    Layer specific heat [J kg-1 K-1]
                    rho (z)                  ::    Layer density [kg m-3]
                    h (z)                    ::    Layer height [m]

        Output:
                    lwc (z)                  ::    Layer liquid water content (updated) [-]
                    icf (z)                  ::    Layer ice fraction (updated) [-]
                    T (z)                    ::    Layer temperature (updated) [K]
                    h (z)                    ::    Layer height (updated) [m]
                    subsurface_melt          ::    Subsurface melt [m w.e.]
                    SW_penetrating           ::    Penetrating shortwave radiation [W m-2]
        
        """

    # Import Sub-surface Grid Information:
    d = GRID.get_depth()

    # Calculate penetrating radiation:
    surface_density = GRID.get_node_density(0)
    if surface_density < snow_ice_threshold:
        SW_penetrating = SW_net * 0.1 # (10 % of net shortwave radiation penetrates a snow surface)
        absorption_distribution = np.exp(extinction_coeff_snow * - np.append(0.0, d))
    else:
        SW_penetrating = SW_net * 0.2 # (20 % of net shortwave radiation penetrates an ice surface)
        absorption_distribution = np.exp(extinction_coeff_ice *  - np.append(0.0, d))

    # Energy flux supplied to subsurface layers:
    Energy_flux = SW_penetrating * np.abs(np.diff(absorption_distribution))

    # Store the cumulative subsurface melt
    subsurface_melt = 0.0

    # Create list of layers to be removed
    layers_to_remove = []

    # Loop over all internal sub-surface grid nodes: (Currently exploring faster vectorisation options)
    for Idx in range(0, GRID.number_nodes - 1):

        # Updated temperature due to absorption of penetrating shortwave radiation
        T = float(GRID.get_node_temperature(Idx) + (Energy_flux[Idx] * dt / (GRID.get_node_density(Idx) * GRID.get_node_specific_heat(Idx) * GRID.get_node_height(Idx))))

        # Subsurface melting occurs if energy flux increases temperature above 0 °C
        if (T - zero_temperature > 0.0):

            # Temperature difference between layer and freezing temperature
            dT = T - zero_temperature

            # Compute conversion factor (1/K)
            Conversion = (spec_heat_ice * ice_density) / (water_density * lat_heat_melting)

            # Maximum subsurface melting based on available ice:
            d_lwc_max_ice = GRID.get_node_ice_fraction(Idx) * (ice_density / water_density)

            # Maximum subsurface melting based on available excess energy:
            d_lwc_max_energy = Conversion * dT * GRID.get_node_ice_fraction(Idx)

            # Subsurface melt (fractional):
            d_lwc = min(d_lwc_max_ice, d_lwc_max_energy)

            # Change in fractional ice content:
            d_icf = d_lwc * (water_density / ice_density)

            # Update cumulative subsurface melt:
            layer_subsurface_melt = d_icf * (ice_density / water_density) * GRID.get_node_height(Idx) # [m w.e.]
            subsurface_melt = subsurface_melt + layer_subsurface_melt

            # Check if entire layer has melted:
            if GRID.get_node_ice_fraction(Idx) - d_icf == 0:

                # Re-allocate layer liquid water content into next layer:
                GRID.set_node_liquid_water_content(Idx + 1, GRID.get_node_liquid_water_content(Idx + 1) + (layer_subsurface_melt / GRID.get_node_height(Idx + 1)))
                                                   
                # Delete layer / node:
                layers_to_remove.append(Idx)

            else:
                # Initial node mass:
                initial_mass =  GRID.get_node_density(Idx) * GRID.get_node_height(Idx)

                # Update sub-surface node properties (temperature, height, volumetric ice fraction & liquid water content):
                GRID.set_node_temperature(Idx, zero_temperature)
                GRID.set_node_liquid_water_content(Idx, GRID.get_node_liquid_water_content(Idx) + d_lwc)
                GRID.set_node_ice_fraction(Idx, GRID.get_node_ice_fraction(Idx) - d_icf)
                GRID.set_node_height(Idx, initial_mass / GRID.get_node_density(Idx)) # Mass conservation
        
        else:
            
            # Set layer temperature to updated value
            GRID.set_node_temperature(Idx, T)

    # Remove melted subsurface layers:
    if layers_to_remove: # (Enables Numba compatibility)
        GRID.remove_node(layers_to_remove)

    return subsurface_melt, SW_penetrating

    # ====================================================================================================================
