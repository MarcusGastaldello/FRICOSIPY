"""
    ==================================================================

                              NODE CLASS FILE

        This file creates and maintains the Node Python Class 
        that stores the state variables of the subsurface layers. 
        This class provides various set / get functions that can
        read or overwrite the state of individual subsurface layers. 

    ==================================================================
"""

import numpy as np
from constants import *
from parameters import *
from collections import OrderedDict
from numba import int32, float64
from numba.experimental import jitclass

# ==================== #
# Numba Specification:
# ==================== #

spec = OrderedDict()
spec['height'] = float64
spec['density'] = float64          
spec['temperature'] = float64
spec['average_temperature'] = float64 
spec['liquid_water_content'] = float64    
spec['refreeze'] = float64
spec['firn_refreeze'] = float64
spec['hydro_year'] = int32
spec['grain_size'] = float64
spec['ice_fraction'] = float64

# =================================================================================================

# =========== #
# Node Class:
# =========== #

@jitclass(spec)
class Node:
    """ The Node Python class stores the state layer variables. The subsurface grid consists of a list of 
    nodes that store the information of individual layers. The class provides various setter/getter functions
    to read or overwrite the state of individual layers. 

        State layer variables:

                Layer height                  ::    Height of the layer [m]
                Layer temperature             ::    Temperature of the layer [K]
                Layer average temperature     ::    Average temperature of the layer [K]
                Layer liquid water content    ::    Volumetric liquid water content of the layer [-]
                Layer refreeze                ::    Refrozen water within the layer [m w.e.]
                Firn layer refreeze           ::    Refrozen water within the layer (whilst firn) [m w.e.]
                Layer hydrological year       ::    Hydrological year of the layer's formation [yyyy]
                Layer grain size              ::    Grain size of the layer [mm]
                Layer ice fraction            ::    Volumetric ice fraction of the layer [-]

    All remaining derived layer variables are then calculated / derived from these state layer variables.

    Note: Firn here is defined as layers that have a hydrological layer at least one year older that the
    current simulation year. The firn layer refreezing variable is used to determine the firn facie.

    """    

    # =============== #
    # Initialisation:
    # =============== #

    def __init__(self, height, snow_density, temperature, average_temperature, liquid_water_content, refreeze, 
                 firn_refreeze, hydro_year, grain_size, ice_fraction = None):
        """ Initialises the Node Python class """

        # Initialise state layer variables 
        self.height = height
        self.temperature = temperature
        self.average_temperature = average_temperature
        self.liquid_water_content = liquid_water_content
        self.refreeze = refreeze
        self.firn_refreeze = firn_refreeze
        self.hydro_year = hydro_year
        self.grain_size = grain_size
        if ice_fraction is None:
            self.ice_fraction = (snow_density - (1 - (snow_density / ice_density)) * air_density) / ice_density
        else:
            self.ice_fraction = ice_fraction

    # ================================================================================================== #

    # ======================================== #
    # Get Functions for State Layer Variables:
    # ======================================== #

    def get_layer_height(self):
        """ Returns the layer height [m] """        
        return self.height
    
    # -----------------------------------------------

    def get_layer_temperature(self):
        """ Returns the layer temperature [K] """
        return self.temperature
    
    # -----------------------------------------------

    def get_average_layer_temperature(self):
        """ Returns the average layer temperature [K] """
        return self.average_temperature
    
    # -----------------------------------------------
    
    def get_layer_ice_fraction(self):
        """ Returns the layer volumetric ice fraction [-] """
        return self.ice_fraction
    
    # -----------------------------------------------
    
    def get_layer_refreeze(self):
        """ Returns the layer refreezing [m w.e.] """
        return self.refreeze
    
    # -----------------------------------------------
    
    def get_firn_layer_refreeze(self):
        """ Returns the firn layer refreezing [m w.e.] """
        return self.firn_refreeze 
    
    # -----------------------------------------------

    def get_layer_liquid_water_content(self):
        """ Returns the layer liquid water content [-] """
        return self.liquid_water_content
    
    # -----------------------------------------------
    
    def get_layer_hydro_year(self):
        """ Returns the layer hydrological year [yyyy] """
        return self.hydro_year
    
    # -----------------------------------------------
    
    def get_layer_grain_size(self):
        """ Returns the layer grain size [mm] """
        return self.grain_size

    # ================================================================================================== #

    # ========================================== #
    # Get Functions for Derived Layer Variables:
    # ========================================== #

    def get_layer_density(self):
        """ Returns the layer density [kg m-3] """
        return self.get_layer_ice_fraction() * ice_density + self.get_layer_liquid_water_content() * water_density + self.get_layer_porosity() * air_density
    
    # -----------------------------------------------

    def get_layer_specific_heat(self):
        """ Returns the layer specific heat capacity [J kg-1 K-1] """
        methods_allowed = ['bulk','Yen81']
        if specific_heat_method == 'bulk':    
            specific_heat = self.get_layer_ice_fraction() * specific_heat_ice + self.get_layer_porosity() * specific_heat_air + self.get_layer_liquid_water_content() * specific_heat_water
        elif specific_heat_method == 'Yen81':
            specific_heat = 152.2 + 7.122 * self.get_layer_temperature()
        else:
            raise ValueError("Specific heat method = \"{:s}\" is not allowed, must be one of {:s}".format(specific_heat_method, ", ".join(methods_allowed)))
        return specific_heat

    # ----------------------------------------------- 
    
    def get_layer_irreducible_water_content(self):
        """ Returns the layer irreducible water content [-] """
        methods_allowed = ['Coleou98','constant']
        if irreducible_water_content_method == 'Coleou98':
            if (self.get_layer_ice_fraction() <= 0.23):
                irr = 0.0264 + 0.0099*((1-self.get_layer_ice_fraction())/self.get_layer_ice_fraction()) 
            elif (self.get_layer_ice_fraction() > 0.23) & (self.get_layer_ice_fraction() <= 0.812):
                irr = 0.08 - 0.1023*(self.get_layer_ice_fraction()-0.03)
            else:
                irr = 0.0
        elif irreducible_water_content_method == 'constant':
            irr = constant_irreducible_water_content 
        else:
            raise ValueError("Irreducible water content method = \"{:s}\" is not allowed, must be one of {:s}".format(irreducible_water_content_method, ", ".join(methods_allowed)))
        return irr

    # ----------------------------------------------- 
    
    def get_layer_cold_content(self):
        """ Returns the layer cold content [J m-2] """
        return -self.get_layer_specific_heat() * self.get_layer_density() * self.get_layer_height() * (self.get_layer_temperature()-zero_temperature)

    # -----------------------------------------------
    
    def get_layer_porosity(self):
        """ Returns the layer porosity [-] """
        return 1 - self.get_layer_ice_fraction() - self.get_layer_liquid_water_content()

    # -----------------------------------------------
   
    def get_layer_thermal_conductivity(self):
        """ Returns the layer thermal conductivity [W m-1 K-1] """
        methods_allowed = ['bulk','empirical','Sturm97','Calonne19']
        if thermal_conductivity_method == 'bulk':
            lam = self.get_layer_ice_fraction() * k_i + self.get_layer_porosity() * k_a + self.get_layer_liquid_water_content() * k_w
        elif thermal_conductivity_method == 'empirical':
            lam = 0.021 + 2.5 * np.power((self.get_layer_density()/1000),2)
        elif thermal_conductivity_method == 'Sturm97':
            lam = 0.138 - 1.01e-3 * self.get_layer_density() + 3.23e-6 * np.power((self.get_layer_density()),2)
        elif thermal_conductivity_method == 'Calonne19': 
            theta = 1 / (1 + np.exp(-2 * 0.02 * (self.get_layer_density() - 450)))
            lam = (theta * (2.107 + 0.003618 * (self.get_layer_density() - ice_density))) + \
                  ((1 - theta) * ((0.024 - (1.23e-4 * self.get_layer_density()) + (2.5e-6 * np.power(self.get_layer_density(),2)))))
        else:
            raise ValueError("Thermal conductivity method = \"{:s}\" is not allowed, must be one of {:s}".format(thermal_conductivity_method, ", ".join(methods_allowed)))
        return lam

    # -----------------------------------------------

    def get_layer_thermal_diffusivity(self):
        """ Returns the layer thermal diffusivity [m2 s-1] """
        return self.get_layer_thermal_conductivity() / (self.get_layer_density() * self.get_layer_specific_heat())
    
    # -----------------------------------------------

    def get_layer_saturation(self):
        """ Returns the layer water saturation [-] 
            Hirashima et al., 2010 (https://doi.org/10.1016/j.coldregions.2010.09.003) - Eqn. (5) 
            Yamaguchi et al., 2010 (https://doi.ord/10.1016/j.coldregions.2010.05.008) - """
        residual_water_content = 0.02
        return min(1,max(0,((self.get_layer_liquid_water_content() - residual_water_content) / \
                  (((snow_ice_threshold - self.get_layer_ice_fraction() * ice_density) / water_density) - residual_water_content))))
    
    # -----------------------------------------------

    def get_layer_saturated_hydraulic_conductivity(self):
        """ Returns the layer saturated hydraulic conductivity [m s-1] 
            Shimizu, 1970 (http://hdl.handle.net/2115/20234) OR
            Calonne et al., 2012 (https://doi.org/10.5194/tc-6-939-2012) """
        methods_allowed = ['Shimizu70','Calonne12']
        if hydraulic_conductivity_method == 'Shimizu70':
            Ks = 0.077 * (self.get_layer_grain_size() / 10) **2 * np.exp(-0.0078 * self.get_layer_density())
        if hydraulic_conductivity_method == 'Calonne12':
            Ks = 3 * (self.get_layer_grain_size() / 2000) ** 2 * 9.82 / 1.79e-06 * np.exp(-0.013 * self.get_layer_density())
        else:
            raise ValueError("Saturated hydraulic conductivity method = \"{:s}\" is not allowed, must be one of {:s}".format(hydraulic_conductivity_method, ", ".join(methods_allowed)))    
        return Ks
    
    # -----------------------------------------------

    def get_layer_hydraulic_conductivity(self):
        """ Returns the layer hydraulic conductivity [m s-1]
            Hirashima et al., 2010 (https://doi.org/10.1016/j.coldregions.2010.09.003),
            Mualem, 1976 (https://doi.org/10.1029/WR012i003p00513),
            van Genuchten, 1980 (https://doi.org/10.2136/sssaj1980.03615995004400050002x) """
        n = 15.68 * np.exp(-0.46 * self.get_layer_grain_size()) + 1
        m = 1 - 1 / n
        Kr = self.get_layer_saturation() ** 0.5 * (1.0 - (1.0 - self.get_layer_saturation() ** (1.0 / m)) ** m) ** 2
        return self.get_layer_saturated_hydraulic_conductivity() * Kr
    
        # Note: could be further developed to represent ice lenses according to Colbeck 1975 (https://doi.org/10.1029/WR011i002p00261).
    
    # -----------------------------------------------

    def get_layer_hydraulic_head(self):
        """ Returns the layer hydraulic suction head [m]
            Hirashima et al., 2010 (http://dx.doi.org/10.1016/j.coldregions.2010.09.003) - Eqns. (9) & (17) """
        n = 15.68 * np.exp(-0.46 * self.get_layer_grain_size()) + 1
        m = 1 - 1 / n
        return 1 / (7.3 * np.exp(1.9)) * (max(self.get_layer_saturation(), 1e-12) ** (-1 / m) - 1) ** (1 / n)

    # ===============================================

    # ======================================== #
    # Set Functions for State Layer Variables:
    # ======================================== #


    def set_layer_height(self, height):
        """ Sets the layer height [m] """
        self.height = height

    # -----------------------------------------------

    def set_layer_temperature(self, temperature):
        """ Sets the layer temperature [K] """
        self.temperature = temperature

    # -----------------------------------------------

    def set_average_layer_temperature(self, average_temperature):
        """ Sets the average layer temperature [K] """
        self.average_temperature = average_temperature

    # -----------------------------------------------
    
    def set_layer_ice_fraction(self, ice_fraction):
        """ Sets the layer volumetric ice fraction [-] """
        self.ice_fraction = ice_fraction

    # -----------------------------------------------
    
    def set_layer_refreeze(self, refreeze):
        """ Sets the layer refreeze [m w.e.] """
        self.refreeze = refreeze

    # -----------------------------------------------
    
    def set_firn_layer_refreeze(self, firn_refreeze):
        """ Sets the firn layer refreeze [m w.e.]"""
        self.firn_refreeze = firn_refreeze    

    # -----------------------------------------------

    def set_layer_liquid_water_content(self, liquid_water_content):
        """ Sets the layer volumetric liquid water content [-] """
        self.liquid_water_content = liquid_water_content

    # -----------------------------------------------

    def set_layer_hydro_year(self, hydro_year):
        """ Sets the layer hydrological year [yyyy] """
        self.hydro_year = hydro_year

        # -----------------------------------------------

    def set_layer_grain_size(self, grain_size):
        """ Sets the layer grain size [mm] """
        self.grain_size = grain_size

    # =============================================================================
