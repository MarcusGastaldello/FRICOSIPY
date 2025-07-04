from constants import *
from parameters import *
import numpy as np

from collections import OrderedDict
from numba import float64  
from numba.experimental import jitclass

spec = OrderedDict()
spec['height'] = float64              
spec['temperature'] = float64     
spec['liquid_water_content'] = float64     
spec['ice_fraction'] = float64
spec['refreeze'] = float64
spec['firn_refreeze'] = float64
spec['hydro_year'] = float64

# =================================================================================================

@jitclass(spec)
class Node:
    """ The Node-class stores the state variables of layer. 
    
    The numerical grid consists of a list of nodes that store the information 
    of individual layers. The class provides various setter/getter functions
    to read or overwrite the state of individual layers. 

    Parameters
    ----------
        height : float
            Height of the layer [:math:`m`]
        temperature : float
            temperature of the layer [:math:`K`]
        liquid_water content: float
            liquid water content [:math:`m~w.e.`]

    Returns
    -------
        Node : :py:class:`cosipy.cpkernel.node` object

    """

    # =============== #
    # Initialisation:
    # =============== #

    def __init__(self, height, snow_density, temperature, liquid_water_content, ice_fraction = None):

        # Initialise state variables 
        self.height = height
        self.temperature = temperature
        self.liquid_water_content = liquid_water_content
        
        if ice_fraction is None:
            # Remove weight of air from density
            a = snow_density - (1 - (snow_density / ice_density)) * air_density
            self.ice_fraction = a / ice_density
        else:
            self.ice_fraction = ice_fraction

        self.refreeze = 0.0
        self.firn_refreeze = 0.0
        self.hydro_year = 0.0

    # ================================================================================================== #

    # ======================================== #
    # Get Functions for State Layer Variables:
    # ======================================== #

    def get_layer_height(self):
        """ Returns the layer height of the node.
        
        Returns
        -------
            height : float
                Snow layer height [:math:`m`]
        """
        return self.height
      
    # -----------------------------------------------

    def get_layer_temperature(self):
        """ Returns the snow layer temperature of the node. 
        
        Returns
        -------
            T : float
                Snow layer temperature [:math:`K`]
        """
        return self.temperature

    # -----------------------------------------------
    
    def get_layer_ice_fraction(self):
        """ Returns the volumetric ice fraction of the node. 
        
        Returns
        -------
            ice_fraction : float
                The volumetric ice fraction [-] 
        """
        return self.ice_fraction

    # -----------------------------------------------
    
    def get_layer_refreeze(self):
        """ Returns the amount of refreezing of the node. 
        
        Returns
        -------
            refreeze : float
                Amount of water that has refrozen per time step [:math:`m~w.e.`]
        """
        return self.refreeze
    
    # -----------------------------------------------
    
    def get_firn_layer_refreeze(self):
        """ Returns the amount of refreezing of a firn node. 
        
        Returns
        -------
            refreeze : float
                Amount of water that has refrozen in firn per time step [:math:`m~w.e.`]
        """
        return self.firn_refreeze

    # -----------------------------------------------   

    def get_layer_liquid_water_content(self):
        """ Returns the liquid water content of the node.

        Returns
        -------
            lwc : float
                Liquid water content [-]
        """
        return self.liquid_water_content
    
    # -----------------------------------------------
    
    def get_layer_hydro_year(self):
        """ Returns the layer year of the node.
        
        Returns
        -------
            year : float
                Snow layer year [yyyy]
        """
        return self.hydro_year

    # ================================================================================================== #

    # ========================================== #
    # Get Functions for Derived Layer Variables:
    # ========================================== #

    def get_layer_density(self):
        """ Returns the mean density including ice and liquid of the node. 

        Returns
        -------
            rho : float
                Snow density [:math:`kg~m^{-3}`]
        """
        return self.get_layer_ice_fraction()*ice_density + self.get_layer_liquid_water_content()*water_density + self.get_layer_air_porosity()*air_density

    # -----------------------------------------------
    
    def get_layer_air_porosity(self):
        """ Returnis the ice fraction of the node.

        Returns
        -------
            porosity : float
                Air porosity [:math:`m`]
        """
        return max(0.0, 1 - self.get_layer_liquid_water_content() - self.get_layer_ice_fraction())

    # -----------------------------------------------
    
    def get_layer_specific_heat(self):
        """ Returns the volumetric averaged specific heat of the node. 

        Returns
        -------
            cp : float
                Specific heat [:math:`J~kg^{-1}~K^{-1}`]
        """
        SHmethods_allowed = ['bulk','Yen81']
        if specific_heat_method == 'bulk':    
            specific_heat = self.get_layer_ice_fraction()*spec_heat_ice + self.get_layer_air_porosity()*spec_heat_air + self.get_layer_liquid_water_content()*spec_heat_water
        elif specific_heat_method == 'Yen81':
            specific_heat = 152.2 + 7.122 * self.get_layer_temperature()
        else:
            raise ValueError("Specific heat method = \"{:s}\" is not allowed, must be one of {:s}".format(specific_heat_method, ", ".join(SHmethods_allowed)))
        return specific_heat

    # -----------------------------------------------

    def get_layer_liquid_water_content(self):
        """ Returns the liquid water content of the node.

        Returns
        -------
            lwc : float
                Liquid water content [-]
        """
        return self.liquid_water_content

    # ----------------------------------------------- 
    
    def get_layer_irreducible_water_content(self):
        """ Returns the irreducible water content of the node. 

        Returns
        -------
            ret : float
                Irreducible water content [-]
        """
        if (self.get_layer_ice_fraction() <= 0.23):
            theta_e = 0.0264 + 0.0099*((1-self.get_layer_ice_fraction())/self.get_layer_ice_fraction()) 
        elif (self.get_layer_ice_fraction() > 0.23) & (self.get_layer_ice_fraction() <= 0.812):
            theta_e = 0.08 - 0.1023*(self.get_layer_ice_fraction()-0.03)
        else:
            theta_e = 0.0
        return theta_e

    # ----------------------------------------------- 
    
    def get_layer_cold_content(self):
        """ Returns the cold content of the node. 

        Returns
        -------
            cc : float
                Cold content [:math:`J~m^{-2}`]
        """
        return -self.get_layer_specific_heat() * self.get_layer_density() * self.get_layer_height() * (self.get_layer_temperature()-zero_temperature)

    # -----------------------------------------------
    
    def get_layer_porosity(self):
        """ Returns the porosity of the node. 

        Returns
        -------
            por : float
                Air porosity [-]
        """
        return 1-self.get_layer_ice_fraction()-self.get_layer_liquid_water_content()

    # -----------------------------------------------
   
    def get_layer_thermal_conductivity(self):
        """ Returns the volumetric weighted thermal conductivity of the node.

        Returns
        -------
            lambda : float
                Thermal conductivity [:math:`W~m^{-1}~K^{-1}`]
        """
        methods_allowed = ['bulk','empirical','Sturm97','Calonne19']
        if thermal_conductivity_method == 'bulk':
            lam = self.get_layer_ice_fraction()*k_i + self.get_layer_air_porosity()*k_a + self.get_layer_liquid_water_content()*k_w
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
        """ Returns the thermal diffusivity of the node. 

        Returns
        -------
            K : float
                Thermal diffusivity [:math:`m^{2}~s^{-1}`]
        """
        K = self.get_layer_thermal_conductivity()/(self.get_layer_density()*self.get_layer_specific_heat())
        return K

    # ===============================================

    # ======================================== #
    # Set Functions for State Layer Variables:
    # ======================================== #


    def set_layer_height(self, height):
        """ Sets the layer height of the node. 
        
        Parameters
        ----------
            height : float
                Layer height [:math:`m`]
        """
        self.height = height

    # -----------------------------------------------

    def set_layer_temperature(self, T):
        """ Sets the mean temperature of the node.

        Parameters
        ----------
            T : float
                Layer temperature [:math:`K`]
        """
        self.temperature = T

    # -----------------------------------------------
    
    def set_layer_ice_fraction(self, ifr):
        """ Sets the ice fraction of the node. 

        Parameters
        ----------
            ifr : float
                Ice fraction [-]
        """
        self.ice_fraction = ifr

    # -----------------------------------------------
    
    def set_layer_refreeze(self, refreeze):
        """ Sets the amount of water refrozen in the node.

        Parameters
        ----------
            refr : float
                Amount of refrozen water [:math:`m~w.e.`]
        """
        self.refreeze = refreeze

    # -----------------------------------------------
    
    def set_firn_layer_refreeze(self, firn_refreeze):
        """ Sets the amount of water refrozen in a firn node.

        Parameters
        ----------
            refr : float
                Amount of refrozen water in a firn node [:math:`m~w.e.`]
        """
        self.firn_refreeze = firn_refreeze    

    # -----------------------------------------------

    def set_layer_liquid_water_content(self, lwc):
        """ Sets the liquid water content of the node.

        Parameters
        ----------
            lwc : float
                Liquid water content [-]
        """
        self.liquid_water_content = lwc

    # -----------------------------------------------

    def set_layer_hydro_year(self, hydro_year):
        """ Sets the layer hydrological year of the node. 
        
        Parameters
        ----------
            hydrological year : float
                Layer hydrological year [yyyy]
        """
        self.hydro_year = hydro_year

    # =============================================================================
