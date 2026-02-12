"""
    ==================================================================

                        PERCOLATION & REFREEZING MODULE

        This module percolates water through subsurface layers and
        either: refreezes it if there is sufficient cold content; 
        stores it if there is sufficient irreducible water content;
        or records any excess as discharge / run-off for a single 
        model timestep.

    ==================================================================
"""

import numpy as np
from numba import njit
from constants import *
from parameters import *
from main.modules.darcy_fluxes import *

# ============================== #
# Water Percolation & Refreezing
# ============================== #

def percolation_refreezing(GRID, hydro_year, surface_water, dt):
    """ This module percolates and refreezes subsurface water """

    # Preferential Percolation:
    if surface_water != 0:
        preferential_percolation_allowed = ['Marchenko17','disabled']
        if preferential_percolation_method == 'Marchenko17':
            method_Marchenko(GRID, surface_water)
        elif preferential_percolation_method == 'disabled':
            GRID.set_node_liquid_water_content(0, GRID.get_node_liquid_water_content(0) + float(surface_water / GRID.get_node_height(0)))
        else:
            raise ValueError("Preferential percolation method = \"{:s}\" is not allowed, must be one of {:s}".format(preferential_percolation_method, ", ".join(preferential_percolation_allowed)))

    # Only run percolation and refreezing modules if water present:
    if (np.any(GRID.get_liquid_water_content()) != 0):

        # Water Percolation, Storage & Run-off:
        standard_percolation_allowed = ['bucket','Darcy']
        if standard_percolation_method == 'bucket':
            Q = method_bucket_scheme(GRID)
        elif standard_percolation_method == 'Darcy':
            Q = method_Darcy(GRID, dt)
        else:
            raise ValueError("Standard percolation method = \"{:s}\" is not allowed, must be one of {:s}".format(standard_percolation_method, ", ".join(standard_percolation_allowed)))

        # Sub-surface Refreezing:
        water_refrozen = refreezing(GRID, hydro_year)

    else:
        Q , water_refrozen = 0, 0

    return Q , water_refrozen

# ====================================================================================================================

# ======================== #
# Preferential Percolation
# ======================== #

@njit
def method_Marchenko(GRID, surface_water):
    """ Statistical preferential percolation scheme (Gaussian)
        after Marchenko et al., 2013 
        
        Parameters:
                    preferential_percolation_depth      ::    Charachteristic preferential percolation depth [m]
        Input:
                    GRID                                ::    Subsurface GRID variables -->
                    h (z)                               ::    Layer height [m]
                    z (z)                               ::    Layer depth [m]
                    lwc (z)                             ::    Layer liquid water content [-]
        Output:
                    lwc (z)                             ::    Layer liquid water content (updated) [-]

    """
    # Import Sub-surface Grid Information:
    h = np.asarray(GRID.get_height()) 
    z = np.asarray(GRID.get_depth())
    lwc = np.asarray(GRID.get_liquid_water_content())

    # Calculate the Gaussian Probability Density Function (PDF):
    PDF_normal = 2 * ((np.exp(- (z**2)/(2 * (preferential_percolation_depth / 3)**2))) / ((preferential_percolation_depth/3) * np.sqrt(2 * np.pi)))
    # Adjust in accordance with sub-surface layer heights:
    PDF_normal_height = PDF_normal * h
    # Normalise by dividing by the cumulative sum:
    Normalise = PDF_normal_height / np.sum(PDF_normal_height)
    # Update layer water content:
    water = lwc + ((Normalise * surface_water)/ h)
    GRID.set_liquid_water_content(water)

# ====================================================================================================================

# =================================== #
# Water Percolation, Storage & Runoff
# =================================== #

# ====================== #
# 'Bucket' Scheme Method
# ====================== #

@njit  
def method_bucket_scheme(GRID):
    """ Percolation of water according to a 'bucket' approach.
    
        Input:
                    GRID       ::    Subsurface GRID variables -->
                    lwc (z)    ::    Layer liquid water content [-] 
                    irr (z)    ::    Layer irreducible water content [-]
                    h (z)      ::    Layer height [m]
        Output:
                    lwc (z)    ::    Layer liquid water content (updated) [-]
                    Q          ::    Runoff [m w.e.]
    
    """

    # Reset output values:
    Q = 0

    # Skip percolation if there is only one subsurface layer:
    if GRID.get_number_layers() > 1:

        # Loop over all internal sub-surface grid nodes: (Currently exploring faster vectorisation options)
        for Idx in range(0, GRID.number_nodes - 1): 

            # Irreducible water content:
            irr = GRID.get_node_irreducible_water_content(Idx)
            # Liquid water content:
            lwc = GRID.get_node_liquid_water_content(Idx)   
            # Residual volumetric fraction of water:
            residual = np.maximum((lwc - irr), 0.0)

            if residual > 0:
                # Set current layer as saturated (at irreducible water content):
                GRID.set_node_liquid_water_content(Idx, irr)
                residual = residual * GRID.get_node_height(Idx)
                GRID.set_node_liquid_water_content(Idx + 1, GRID.get_node_liquid_water_content(Idx + 1) + residual / GRID.get_node_height(Idx + 1))
            else:
                # Set current layer with unsaturated water content:
                GRID.set_node_liquid_water_content(Idx, lwc)

    # Water in the last sub-surface node is allocated to run-off:
    Q = GRID.get_node_liquid_water_content(GRID.number_nodes - 1) * GRID.get_node_height(GRID.number_nodes - 1)
    GRID.set_node_liquid_water_content(GRID.number_nodes - 1, 0.0)

    return Q

# --------------------------------------------------------------------------------------------------------------------

# ================= #
# Darcy Flow Method
# ================= #

@njit  
def method_Darcy(GRID, dt):
    """ Percolation of water according to a 'Darcy's law' based approach 
        according to Hirashima et al., (2010) (https://doi.org/10.1016/j.coldregions.2010.09.003)
    
        Input:
                    GRID       ::    Subsurface GRID variables -->
                    K (z)      ::    Layer hydraulic conductivity [m s-1]
                    d (z)      ::    Layer grain size [mm]
                    h (z)      ::    Layer height [m]
                    lwc (z)    ::    Layer liquid water content [-] 
                    irr (z)    ::    Layer irreducible water content [-]
                    theta (z)  ::    Layer unsaturated hydrualic conductivity [m s-1]
        Output:
                    lwc (z)    ::    Layer liquid water content (updated) [-]
                    Q          ::    Runoff [m w.e.]
    
    """

    dt_cumulative = 0.0

    while dt_cumulative < dt:

        # Import Sub-surface Grid Information:
        h = np.asarray(GRID.get_height())
        d = np.asarray(GRID.get_grain_size())
        theta = np.minimum(np.maximum(np.asarray(GRID.get_hydraulic_conductivity()),1e-10), 0.999)

        # Inverse moisture gradient (C)
        n = 15.68 * np.exp(-0.46 * d) + 1
        m = 1 - 1 / n
        inv_C = (1 / (7.3 * np.exp(1.9) * n * m)) * (theta **(-1 / m - 1)) * ((theta **(-1 / m) - 1)**(1 / n - 1))

        # Determine integration steps required in the solver to ensure numerical stability:
        dt_stable = max(np.min((0.5 * h**2) / (2 * (theta * inv_C) + 1e-12)), 1) # Courant-Friedrichs-Lewy (CFL) stability criterion     

        # Integration timestep:
        dt_step = np.minimum(dt_stable, dt - dt_cumulative)
        dt_cumulative += dt_step

        # Calculate water fluxes according to Darcy's law:
        D = darcy_fluxes(GRID, dt_step)

        # Surface node:
        GRID.set_node_liquid_water_content(0, (GRID.get_node_liquid_water_content(0) * GRID.get_node_height(0) + - D[0]) / GRID.get_node_height(0))

        # Intermediate nodes:
        for Idx in range(1, GRID.number_nodes - 1):
            GRID.set_node_liquid_water_content(Idx, (GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx) + (D[Idx - 1] - D[Idx])) / GRID.get_node_height(Idx))

        # Base node:
        Idx = GRID.number_nodes - 1
        GRID.set_node_liquid_water_content(Idx, (GRID.get_node_liquid_water_content(Idx) * GRID.get_node_height(Idx) + D[Idx - 1]) / GRID.get_node_height(Idx))
    
    # Water in the last sub-surface node is allocated to run-off:
    Q = GRID.get_node_liquid_water_content(GRID.number_nodes - 1) * GRID.get_node_height(GRID.number_nodes - 1)
    GRID.set_node_liquid_water_content(GRID.number_nodes - 1, 0.0)

    return Q
            

# ====================================================================================================================

# ====================== #
# Sub-surface Refreezing
# ====================== #

@njit
def refreezing(GRID, year):
    """ Refreezing of subsurface water if a layer has sufficient volumetric capacity and cold content.
            
        Input:
                    GRID              ::    Subsurface GRID variables -->
                    lwc (z)           ::    Layer liquid water content [-] 
                    icf (z)           ::    Layer ice fraction [-]
                    T (z)             ::    Layer temperature [K]
        Output:
                    lwc (z)           ::    Layer liquid water content (updated) [-]
                    icf (z)           ::    Layer ice fraction (updated) [-]
                    T (z)             ::    Layer temperature (updated) [K]
                    water_refrozen    ::    Refrozen water [m w.e.]
    
    """

    # Maximum snow fractional ice content:
    icf_max = (snow_ice_threshold - air_density) / (ice_density - air_density)

    # Import Sub-surface Grid Information:
    lwc = np.asarray(GRID.get_liquid_water_content())
    icf = np.asarray(GRID.get_ice_fraction())     
    T = np.asarray(GRID.get_temperature())
    h = np.asarray(GRID.get_height())
    hydro_year = np.asarray(GRID.get_hydro_year())

    # Volumetric/density limit on refreezing:
    d_lwc_max_density = ((icf_max - icf) * (ice_density/water_density))

    # Temperature difference between layer and freezing temperature, cold content in temperature
    dT_max = np.abs(T - zero_temperature) # (Positive T)

    # Compute conversion factor (1/K)
    Conversion = ((specific_heat_ice * ice_density) / (water_density * latent_heat_melting))

    # Cold content limit on refreezing:
    d_lwc_max_coldcontent = np.where(dT_max < 0 , 0, (icf * Conversion * dT_max) / (1 - (Conversion * dT_max * (water_density / ice_density))))

    # Water refreeze amount (fractional):
    d_lwc = np.asarray([min(x,y,z) for x,y,z in zip(lwc, d_lwc_max_density, d_lwc_max_coldcontent)]) # Numba incompatible with np.min(axis = 1)
    
    # Update sub-surface node volumetric ice fraction and liquid water content:
    GRID.set_liquid_water_content((lwc - d_lwc)) 
    d_icf = d_lwc * (water_density / ice_density)
    icf += d_icf
    GRID.set_ice_fraction(icf)

    # Update sub-surface node temperature for latent heat release:
    dT = d_lwc / (Conversion * icf)
    GRID.set_temperature(T + dT)

    # Record amount of refreezing in all layers:
    GRID.set_refreeze(d_icf * h)
    
    # Record amount of refreezing in firn layers (i.e. all layers except current accumulation year)
    GRID.set_firn_refreeze(np.where(hydro_year != year, d_icf * h, 0))
    
    # Record total water refrozen:
    water_refrozen =  np.sum(d_lwc * h)

    return water_refrozen

# ====================================================================================================================
