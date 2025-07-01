import numpy as np
from numba import njit
from constants import *
from parameters import *

# ============================== #
# Water Percolation & Refreezing
# ============================== #

@njit
def percolation_refreezing(GRID, hydro_year, surface_water):

    # Preferential Percolation:
    if surface_water != 0:
        distribute_water(GRID, surface_water)

    # Sub-surface Refreezing:
    water_refrozen = refreezing(GRID, hydro_year)

    # Water Percolation, Storage & Run-off:
    Q = percolate_water(GRID)

    return Q , water_refrozen

# ====================================================================================================================

# ======================== #
# Preferential Percolation
# ======================== #

@njit
def distribute_water(GRID, surface_water):

    # Import Sub-surface Grid Information:
    h = np.asarray(GRID.get_height()) 
    z = np.asarray(GRID.get_depth())

    if preferential_percolation_method == 'Marchenko17':
        """ Statistical preferential percolation scheme (Gaussian) (Marchenko et al., 2013) """

        # Calculate the Gaussian Probability Density Function (PDF):
        PDF_normal = 2 * ((np.exp(- (z**2)/(2 * (z_lim / 3)**2))) / ((z_lim/3) * np.sqrt(2 * np.pi)))
        # Adjust in accordance with sub-surface layer heights:
        PDF_normal_height = PDF_normal * h
        # Normalise by dividing by the cumulative sum:
        Normalise = PDF_normal_height / np.sum(PDF_normal_height)
        # Update layer water content:
        water = np.asarray(GRID.get_liquid_water_content()) + ((Normalise * surface_water)/ h)
        GRID.set_liquid_water_content(water)

    elif preferential_percolation_method == 'disabled':

        # Add all water to the uppermost sub-surface layer:
        water = surface_water / GRID.get_node_height(0)
        GRID.set_node_liquid_water_content(0, GRID.get_node_liquid_water_content(0) + float(water))

# ====================================================================================================================

# ====================== #
# Sub-surface Refreezing
# ====================== #

# Note: Numba is not compatible with np.min(axis = 0)
@njit
def refreezing(GRID, hydro_year):

    # Reset output values:
    water_refrozen = 0
    # Maximum snow fractional ice content:
    phi_ice_max = (snow_ice_threshold - air_density) / (ice_density - air_density)

    # Import Sub-surface Grid Information:
    lwc = np.asarray(GRID.get_liquid_water_content())
    icf = np.asarray(GRID.get_ice_fraction())     
    T = np.asarray(GRID.get_temperature())

    # Available water for refreezing:
    available_water = lwc

    # Volumetric/density limit on refreezing:
    d_phi_water_max_density = ((phi_ice_max - icf) * (ice_density/water_density))

    # Temperature difference between layer and freezing temperature, cold content in temperature
    dT_max = np.abs(T - zero_temperature) # (Positive T)

    # Compute conversion factor (1/K)
    Conversion = ((spec_heat_ice * ice_density) / (water_density * lat_heat_melting))

    # Cold content limit on refreezing:
    d_phi_water_max_coldcontent = np.where(dT_max < 0 , 0, (icf * Conversion * dT_max) / (1 - (Conversion * dT_max * (water_density / ice_density))))

    # Water refreeze amount:
    d_phi_water = d_phi_water = np.asarray([min(x,y,z) for x,y,z in zip(available_water,d_phi_water_max_density,d_phi_water_max_coldcontent)])
    # d_phi_water = np.min(np.vstack((available_water,d_phi_water_max_density,d_phi_water_max_coldcontent)), axis = 0) (Note: Numba is not compatible with np.min(axis = 0))
    
    # Update sub-surface node volumetric ice fraction and liquid water content:
    GRID.set_liquid_water_content((lwc - d_phi_water)) 
    d_phi_ice = d_phi_water * (water_density/ice_density)
    GRID.set_ice_fraction((np.asarray(GRID.get_ice_fraction()) + d_phi_ice))

    # Update sub-surface node temperature for latent heat release:
    dT = d_phi_water / (Conversion * np.asarray(GRID.get_ice_fraction()))
    GRID.set_temperature(T + dT)

    # Record amount of refreezing in layers:
    GRID.set_refreeze(d_phi_ice * np.asarray(GRID.get_height()))
    
    # Record amount of refreezing in firn layers (i.e. all layers except current accumulation year)
    GRID.set_firn_refreeze(np.where(np.asarray(GRID.get_hydro_year()) != hydro_year, d_phi_ice * np.asarray(GRID.get_height()), 0))
    
    # Record total water refrozen:
    water_refrozen =  np.sum(d_phi_water * np.asarray(GRID.get_height()))

    return water_refrozen

# ====================================================================================================================

# =================================== #
# Water Percolation, Storage & Runoff
# =================================== #

@njit  
def percolate_water(GRID):

    # Reset output values:
    Q = 0

    # Loop over all internal sub-surface grid nodes:
    for Idx in range(0, GRID.number_nodes - 1): 

        # Irreducible water content:
        phi_irreducible = GRID.get_node_irreducible_water_content(Idx)
        # Liquid water content:
        phi_water = GRID.get_node_liquid_water_content(Idx)   
        # Residual volumetric fraction of water:
        residual = np.maximum((phi_water - phi_irreducible), 0.0)

        if residual > 0:
            # Set current layer as saturated (at irreducible water content):
            GRID.set_node_liquid_water_content(Idx, phi_irreducible)
            residual = residual * GRID.get_node_height(Idx)
            GRID.set_node_liquid_water_content(Idx + 1, GRID.get_node_liquid_water_content(Idx + 1) + residual / GRID.get_node_height(Idx + 1))
        else:
            # Set current layer with unsaturated water content:
            GRID.set_node_liquid_water_content(Idx, phi_water)

    # Water in the last sub-surface node is allocated to run-off:
    Q = GRID.get_node_liquid_water_content(GRID.number_nodes - 1) * GRID.get_node_height(GRID.number_nodes - 1)
    GRID.set_node_liquid_water_content(GRID.number_nodes - 1, 0.0)

    return Q

# ====================================================================================================================

