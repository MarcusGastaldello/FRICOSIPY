"""
    ==================================================================

                            GRID CLASS FILE

        This file creates and maintains the Grid Python Class 
        that controls the numerical mesh of the subsurface grid.

    ==================================================================
"""

import os
import numpy as np
from constants import *
from parameters import *
from config import *
from main.kernel.node import *
from collections import OrderedDict
from numba import types, typed, intp, int32, float64, optional
from numba.experimental import jitclass

# ==================== #
# Numba Specification:
# ==================== #

node_type = Node.class_type.instance_type
spec = OrderedDict()
spec['layer_heights'] = float64[:]
spec['layer_densities'] = float64[:]
spec['layer_temperatures'] = float64[:]
spec['average_layer_temperatures'] = float64[:]
spec['layer_liquid_water_content'] = float64[:]
spec['layer_refreezes'] = float64[:]
spec['layer_firn_refreezes'] = float64[:]
spec['layer_hydro_years'] = int32[:]
spec['layer_grain_sizes'] = float64[:]
spec['layer_ice_fraction'] = optional(float64[:])
spec['number_nodes'] = intp
spec['old_snow_age'] = float64
spec['old_snow_albedo'] = float64
spec['old_snow_SWE'] = float64
spec['fresh_snow_age'] = float64
spec['fresh_snow_albedo'] = float64
spec['fresh_snow_SWE'] = float64
spec['base_elevation'] = float64
spec['grid'] = types.ListType(node_type)

# ================================================================================================== #

# =========== #
# Grid Class:
# =========== #

@jitclass(spec)
class Grid:     
    """ The Grid Python class forms the subsurface numerical mesh, consisting of a list of nodes that 
        store the information of individual layers. The class provides various setter/getter functions
        to read or overwrite the state of individual layers. 

        Variables:

                Layer heights (z)                 ::    Height of the layers [m]
                Layer temperatures (z)            ::    Temperature of the layers [K]
                Average layer temperatures (z)    ::    Average temperature of the layers [K]
                Layer liquid water contents (z)   ::    Volumetric liquid water content of the layers [-]
                Layer refreezes (z)               ::    Refrozen water within the layers [m w.e.]
                Firn layer refreezes (z)          ::    Refrozen water within the layers (whilst firn) [m w.e.]
                Layer hydrological years (z)      ::    Hydrological year of the layers' formation [yyyy]
                Layer grain sizes (z)             ::    Grain size of the layers [mm]
                Layer ice fractions (z)           ::    Volumetric ice fraction of the layers [-]

        Properties:

                Old snow age         ::    Age of old snow [s] 
                Old snow albedo      ::    Albedo of old snow [-] 
                Old snow SWE         ::    Snow Water Equivalent (SWE) of old snow [m] 
                Fresh snow age       ::    Age of fresh snow [s] 
                Fresh snow albedo    ::    Albedo of fresh snow [-] 
                Fresh snow SWE       ::    Snow Water Equivalent (SWE) of fresh snow [m] 
                Base elevation       ::    Elevation of the bottom of the simulation [m a.s.l.] (used to track the absolute height of the glacier)

        Note 1: The fresh and old snow properties here are independant from the subsurface layers; they track the time since specific snowfall events for the albedo calculation   

        Note 2: Firn here is defined as layers that have a hydrological layer at least one year older that the
        current simulation year. The firn layer refreezing variable is used to determine the firn facie.

        """

    # =============== #
    # Initialisation:
    # =============== #

    def __init__(self, layer_heights, layer_densities, layer_temperatures, average_layer_temperatures, layer_liquid_water_content, 
                 layer_refreezes, layer_firn_refreezes, layer_hydro_years, layer_grain_sizes, base_elevation, layer_ice_fraction = None,
                 old_snow_age = None, old_snow_albedo = None, old_snow_SWE = None, fresh_snow_age = None, fresh_snow_albedo = None, fresh_snow_SWE = None):
        """ Initialises the Grid Python class """

        # Set class variables
        self.layer_heights = layer_heights
        self.layer_densities = layer_densities
        self.layer_temperatures = layer_temperatures
        self.average_layer_temperatures = average_layer_temperatures
        self.layer_liquid_water_content = layer_liquid_water_content
        self.layer_refreezes = layer_refreezes
        self.layer_firn_refreezes = layer_firn_refreezes 
        self.layer_hydro_years = layer_hydro_years
        self.layer_grain_sizes = layer_grain_sizes
        self.layer_ice_fraction = layer_ice_fraction 

        # Number of total nodes
        self.number_nodes = len(layer_heights)

        # Initialise the subsurface grid properties:
        if (old_snow_age is not None) and (old_snow_albedo is not None) and (old_snow_SWE is not None) and (fresh_snow_age is not None) and (fresh_snow_albedo is not None) and (fresh_snow_SWE is not None):
            self.old_snow_age = old_snow_age
            self.old_snow_albedo = old_snow_albedo
            self.old_snow_SWE = old_snow_SWE     
            self.fresh_snow_age = fresh_snow_age
            self.fresh_snow_albedo = fresh_snow_albedo
            self.fresh_snow_SWE = fresh_snow_SWE
        else:
            self.old_snow_age = 0.0
            self.old_snow_albedo = albedo_fresh_snow
            self.old_snow_SWE = 0.0      
            self.fresh_snow_age = 0.0
            self.fresh_snow_albedo = albedo_fresh_snow
            self.fresh_snow_SWE = 0.0
        self.base_elevation = base_elevation

        # Do the grid initialization
        self.grid = typed.List.empty_list(node_type)

        self.init_grid()

    # ================================================================================================= #

    # =============== #
    # Initialise GRID
    # =============== #

    def init_grid(self):
        """ Initialises the subsurface grid according to the initial conditions """
        for idx in range(self.number_nodes):
            layer_ice_fraction = None
            if self.layer_ice_fraction is not None:
                layer_ice_fraction = self.layer_ice_fraction[idx]
            self.grid.append(Node(self.layer_heights[idx], 
                                  self.layer_densities[idx],
                                  self.layer_temperatures[idx],
                                  self.average_layer_temperatures[idx],
                                  self.layer_liquid_water_content[idx], 
                                  self.layer_refreezes[idx],
                                  self.layer_firn_refreezes[idx],
                                  self.layer_hydro_years[idx],
                                  self.layer_grain_sizes[idx],
                                  layer_ice_fraction))

    # ================================================================================================= #

    # ==================== #
    # Add Fresh Snow Layer
    # ==================== #

    def add_fresh_snow(self, height, density, temperature, hydro_year, grain_size):
        """ Adds a new fresh snow layer(node) at the top of the numerical mesh / subsurface grid 

        Variables:

                Layer height                  ::    Height of the new fresh snow layer [m]
                Layer density                 ::    Density of the new fresh snow layer [kg m-3]
                Layer temperature             ::    Temperature of the new fresh snow layer [K]
                Layer hydrological year       ::    Hydrological year of the new fresh snow layer's formation [yyyy]
                Layer grain size              ::    Grain size of the new fresh snow layer [mm]

        Note: The layer ice fraction is determined when the Node class for the new layer is initialised.
        
        """
        # Initialise remaining layer variables as zero
        liquid_water_content = 0.0
        refreeze = 0.0
        firn_refreeze = 0.0

        # Insert new node to the numerical mesh / grid
        self.grid.insert(0, Node(height, density, temperature, temperature, liquid_water_content, refreeze, firn_refreeze, hydro_year, grain_size, None))

        # Increase node counter
        self.number_nodes += 1

        # Set the fresh snow properties for albedo calculation
        SWE = height * (density / water_density)
        self.set_fresh_snow_props(SWE)

    # ================================================================================================= #

    # =================== #
    # Remove Layer / Node
    # =================== #

    def remove_node(self, idx = None):
        """ Removes a layer from the numerical mesh / subsurface grid at node idx """

        # Remove node from list (when there is at least one node)
        if not self.grid:
            pass
        else:
            if idx is None:
                self.grid.pop(0)
            else:
                for index in sorted(idx, reverse=True):
                    del self.grid[index]

            # Decrease node counter
            self.number_nodes -= len(idx)

    # ================================================================================================= #

    # ==================== #
    # Merge Layers / Nodes
    # ==================== #

    def merge_nodes(self, idx):
        """ Merges two subsequent nodes (idx & idx + 1) and combines their properties """

        # Updated layer height
        new_height = self.get_node_height(idx) + self.get_node_height(idx + 1)

        # Updated liquid water content
        new_liquid_water_content = (self.get_node_liquid_water_content(idx) * self.get_node_height(idx) + \
                                    self.get_node_liquid_water_content(idx+1) * self.get_node_height(idx + 1)) / new_height

        # Updated ice fraction
        new_ice_fraction = ((self.get_node_ice_fraction(idx) * self.get_node_height(idx) + \
                            self.get_node_ice_fraction(idx+1) * self.get_node_height(idx + 1)) / new_height)

        # Updated temperature
        new_temperature = (self.get_node_height(idx)/new_height) * self.get_node_temperature(idx) + \
                            (self.get_node_height(idx+1)/new_height) * self.get_node_temperature(idx + 1)
        
        # Updated average temperature
        new_average_temperature = (self.get_node_height(idx)/new_height) * self.get_average_node_temperature(idx) + \
                            (self.get_node_height(idx+1)/new_height) * self.get_average_node_temperature(idx + 1)
        
        # Updated refreezing
        new_refreeze = self.get_node_refreeze(idx) + self.get_node_refreeze(idx + 1)
        new_firn_refreeze = self.get_firn_node_refreeze(idx) + self.get_firn_node_refreeze(idx + 1)

        # Updated grain size
        new_grain_size = (self.get_node_height(idx)/new_height) * self.get_node_grain_size(idx) + \
                            (self.get_node_height(idx+1)/new_height) * self.get_node_grain_size(idx + 1)
        
        # Update the node properties
        self.update_node(idx, new_height, new_temperature, new_average_temperature, new_ice_fraction, new_liquid_water_content, new_refreeze, new_firn_refreeze, new_grain_size)
        
        # Remove the second layer
        self.remove_node([idx+1])

    # =================================================================================================

    # ====================== #
    # Remesh Subsurface Grid
    # ====================== #    

    def update_grid(self):
        """ Re-meshes the layers (numerical grid) """
                     
        self.lagrangian_profile()

    # =================================================================================================

    def lagrangian_profile(self):
        """ Remeshes the subsurface numerical mesh / grid according to a threshold height Lagrangian 
        scheme. New snowfall is accumulated in the uppermost layer until a fixed threshold height is
        attained. At this point a new layer is created and all remaining layers are shifted downwards.
        Beyond the user-defined region of interest, layers are merged into a coarser mesh to improve 
        computational efficiency.
        """
        
        # Merge uppermost layer with the second layer unless it exceeds the maximum layer height or they are from different hydrological years
        if (self.get_number_layers() >= 2):  
            if ((self.get_node_height(0) + self.get_node_height(1) <= maximum_simulation_layer_height) and (self.get_node_hydro_year(0) == self.get_node_hydro_year(1))):
                self.merge_nodes(0)

        # Merge layers if they subseed the minimum snow layer height and become too small  
        indices = np.where(np.asarray(self.get_height()) < minimum_snow_layer_height)[0]
        for i in range(len(indices) - 1, -1, -1): # backwards loop to avoid 
            idx = indices[i]
            if idx < self.get_number_layers() - 1:
                self.merge_nodes(idx)
        
        # Merge into coarser layers if a layer goes beyond the region of interest:
        idx = np.searchsorted(self.get_depth(), coarse_layer_threshold, side="right")
        if (idx + 1 <= (self.get_number_layers() - 1)): 
            if (self.get_node_height(idx) + self.get_node_height(idx + 1) <= maximum_coarse_layer_height):
                self.merge_nodes(idx)

        # If last layer depth exceeds the desired subsurface measurement depth, remove it:
        idx = self.get_number_layers() - 1
        if (self.get_depth()[idx] > max_depth):

            # Update base elevation of computational grid now that the las subsurface layer is to be removed:
            self.set_base_elevation(self.get_base_elevation() + self.get_node_height(-1))

            # Remove the last layer:
            self.remove_node([idx])
        
    # =================================================================================================

    # ===================== #
    # Update Node Variables
    # ===================== #

    def update_node(self, idx, height, temperature, average_temperature, ice_fraction, liquid_water_content, refreeze, firn_refreeze, grain_size):
        """ Updates the properties of a specific layer at node idx 

        Variables:

                Layer height                  ::    Updated height of the layer [m]
                Layer temperature             ::    Updated temperature of the layer [K]
                Layer average temperature     ::    Updated average temperature of the layer [K]
                Layer ice fraction            ::    Updated volumetric ice fraction of the layer [-]
                Layer liquid water content    ::    Updated volumetric liquid water content of the layer [-]
                Layer refreeze                ::    Updated refrozen water within the layer [m w.e.]
                Layer firn refreeze           ::    Updated refrozen water within the layer (whilst firn) [m w.e.]
                Layer grain size              ::    Updated grain size of the layer [mm]        
        
        """

        self.set_node_height(idx,height)
        self.set_node_temperature(idx,temperature)
        self.set_node_average_temperature(idx,average_temperature)
        self.set_node_ice_fraction(idx,ice_fraction)
        self.set_node_liquid_water_content(idx,liquid_water_content)
        self.set_node_refreeze(idx,refreeze)
        self.set_firn_node_refreeze(idx,firn_refreeze)
        self.set_node_grain_size(idx,grain_size)

    # =================================================================================================

    # ================= #
    # Check GRID Layers
    # ================= #

    def check(self, name):
        """ This function checks whether temperature and layer heights are within the valid range """
        if np.min(self.get_height()) < 0.01:
            print(name)
            print('Layer height is smaller than the user defined minimum new_height')
            print(self.get_height())
            print(self.get_density())
        if np.max(self.get_temperature()) > 273.2:
            print(name)
            print('Layer temperature exceeds 273.16 K')
            print(self.get_temperature())
            print(self.get_density())

    # =================================================================================================

    # ================= #
    # Remove Layer Mass
    # ================= #

    def remove_mass(self, mass, idx = 0):
        """ Removes mass from a layer at node idx """

        while mass > 0:
            # Get Snow Water Equivalent (SWE) of layer:
            layer_SWE = self.get_node_height(idx) * (self.get_node_density(idx) / water_density)
            
            # Remove melt from top layer and set new snowheight
            if (mass < layer_SWE):
                self.set_node_height(idx, (layer_SWE - mass) / (self.get_node_density(idx) / water_density))
                mass = 0.0

            # Remove first layer otherwise and continue loop with next layer down
            elif (mass >= layer_SWE):
                self.remove_node([idx])
                mass = mass - layer_SWE

                # If all layers are melted, terminate the loop and ultimately the node simulation
                if self.get_number_layers() == 0:
                    break

        # Keep track of the fresh snow layer (albedo calculation)
        if (idx == 0):
            if self.fresh_snow_SWE - mass > 0:
                # Remove mass (SWE) from fresh snow
                self.set_fresh_snow_props_SWE(self.fresh_snow_SWE - mass)
            else:
                # Fresh snow layer has melted; transfer to old snow layer beneath    
                self.set_fresh_snow_props_to_old_props()

    # ================================================================================================== #

    #======================== #
    # GRID Property Functions
    #======================== #

    """ The albedo module retains information about the age of the fresh snow and underlying layers in order
        to determine the surface albedo. This is independant from the mesh size of the subsurface grid."""

    def set_fresh_snow_props(self, SWE):
        """ Creates a fresh snow layer and records its properites """
        if self.fresh_snow_age < 86400:
            # If fresh snow layer is less than 24 hours old (86400 s), merge the new snow into the fresh snow layer but reset the snow age.
            self.fresh_snow_age = 0
            self.fresh_snow_SWE += SWE
        else:
            # Otherwise, create a new fresh snow layer and move the existing properties to the old underlying snow layer.
            self.old_snow_age = self.fresh_snow_age
            self.old_snow_SWE = self.fresh_snow_SWE 
            self.fresh_snow_age = 0
            self.fresh_snow_SWE = SWE

    def set_fresh_snow_props_SWE(self, SWE):
        """ Updates the fresh snow Snow Water Equivalent (SWE) property """        
        self.fresh_snow_SWE = SWE

    def set_fresh_snow_albedo(self, albedo):
        """ Updates the fresh snow albedo property """
        self.fresh_snow_albedo = albedo

    def set_fresh_snow_props_to_old_props(self):
        """ Resets the age of the fresh snow properties back to the age of the underlying snow layer """
        self.fresh_snow_age = self.old_snow_age
        self.fresh_snow_albedo = self.old_snow_albedo
        self.fresh_snow_SWE = self.old_snow_SWE

    def set_fresh_snow_props_update_time(self, seconds):
        """ Updates the timestamp of the fresh snow layer """
        self.old_snow_age = self.old_snow_age + seconds
        self.fresh_snow_age = self.fresh_snow_age + seconds

    def get_fresh_snow_props(self):
        """ Returns the properties of the fresh snow layer """
        return self.fresh_snow_age, self.fresh_snow_albedo, self.fresh_snow_SWE
    
    # ---------------------------------------------- #
    
    def set_base_elevation(self, base_elevation):
        """ Sets the base elevation of the computational domain [m a.s.l.]"""
        self.base_elevation = base_elevation

    def get_base_elevation(self):
        """ Gets the base elevation of the computational domain [m a.s.l.]"""
        return self.base_elevation

    # ================================================================================================== #

    # ================================= #
    # Set Functions for Layer Variables
    # ================================= #

    def set_node_temperature(self, idx, temperature):
        """ Sets the layer temperature at node idx [K] """
        self.grid[idx].set_layer_temperature(temperature)

    def set_temperature(self, temperature):
        """ Sets the layer temperature profile [K] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_temperature(temperature[idx])

    def set_node_average_temperature(self, idx, average_temperature):
        """ Sets the average layer temperature at node idx [K] """
        self.grid[idx].set_average_layer_temperature(average_temperature)

    def set_average_temperature(self, average_temperature):
        """ Sets the average layer temperature profile [K] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_average_layer_temperature(average_temperature[idx])

    # ---------------------------------------------- #

    def set_node_height(self, idx, height):
        """ Sets the layer height of node idx [m] """
        self.grid[idx].set_layer_height(height)

    def set_height(self, height):
        """ Sets the layer height profile [m] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_height(height[idx])

    # ---------------------------------------------- #

    def set_node_liquid_water_content(self, idx, liquid_water_content):
        """ Sets the layer liquid water content of node idx [-] """
        self.grid[idx].set_layer_liquid_water_content(liquid_water_content)

    def set_liquid_water_content(self, liquid_water_content):
        """ Sets the layer liquid water content profile [-] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_liquid_water_content(liquid_water_content[idx])

    # ---------------------------------------------- #

    def set_node_ice_fraction(self, idx, ice_fraction):
        """ Sets the layer ice fraction of node idx [-] """
        self.grid[idx].set_layer_ice_fraction(ice_fraction)

    def set_ice_fraction(self, ice_fraction):
        """ Sets the layer ice fraction profile [-] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_ice_fraction(ice_fraction[idx])

    # ---------------------------------------------- #

    def set_node_refreeze(self, idx, refreeze):
        """ Sets the layer refreezing of node idx [m w.e.] """
        self.grid[idx].set_layer_refreeze(refreeze)

    def set_refreeze(self, refreeze):
        """ Sets the layer refreezing profile [m w.e.] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_refreeze(refreeze[idx])

    def set_firn_node_refreeze(self, idx, firn_refreeze):
        """ Sets the firn layer refreezing of node idx [m w.e.] """
        self.grid[idx].set_firn_layer_refreeze(firn_refreeze)

    def set_firn_refreeze(self, firn_refreeze):
        """ Sets the firn layer refreezing profile [m w.e.] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_firn_layer_refreeze(firn_refreeze[idx])

    # ---------------------------------------------- #     

    def set_node_hydro_year(self, idx, hydro_year):
        """ Sets the layer hydrological year of node idx [yyyy] """
        self.grid[idx].set_layer_hydro_year(hydro_year)

    def set_hydro_year(self, hydro_year):
        """ Sets the layer hydrological year profile [yyyy] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_hydro_year(hydro_year[idx])

    # ---------------------------------------------- #     

    def set_node_grain_size(self, idx, grain_size):
        """ Sets the layer snow grain size of node idx [mm] """
        self.grid[idx].set_layer_grain_size(grain_size)

    def set_grain_size(self, grain_size):
        """ Sets the layer snow grain sizes profile [mm] (z) """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_grain_size(grain_size[idx])

    # ================================================================================================== #

    # ================================= #
    # Get Functions for Layer Variables
    # ================================= #

    def get_node_temperature(self, idx):
        """ Returns the layer temperature of node idx [K] """
        return self.grid[idx].get_layer_temperature()
    
    def get_temperature(self):
        """ Returns the layer temperature profile [K] (z) """
        return [self.grid[idx].get_layer_temperature() for idx in range(self.number_nodes)]
    
    def get_average_node_temperature(self, idx):
        """ Returns the average layer temperature of node idx [K] """
        return self.grid[idx].get_average_layer_temperature()
    
    def get_average_temperature(self):
        """ Returns the average_layer temperature profile [K] (z) """
        return [self.grid[idx].get_average_layer_temperature() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_specific_heat(self, idx):
        """ Returns the layer specific heat of node idx [J kg-1 K-1] """
        return self.grid[idx].get_layer_specific_heat()

    def get_specific_heat(self):
        """ Returns the layer specific heat profile [J kg-1 K-1] (z) """
        return [self.grid[idx].get_layer_specific_heat() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_height(self, idx):
        """ Returns the layer height of node idx [m] """
        return self.grid[idx].get_layer_height()

    def get_height(self):
        """ Returns the layer height profile [m] (z) """
        return [self.grid[idx].get_layer_height() for idx in range(self.number_nodes)]

    def get_snow_heights(self):
        """ Returns the snow layer height profile [m] (z) """
        return [self.grid[idx].get_layer_height() for idx in range(self.get_number_snow_layers())]

    def get_ice_heights(self):
        """ Returns the ice / glacier layer height profile [m] (z) """
        return [self.grid[idx].get_layer_height() for idx in range(self.number_nodes) if (self.get_node_density(idx) >= snow_ice_threshold)]
    
    # ---------------------------------------------- #

    def get_node_density(self, idx):
        """ Returns the layer density of node idx [kg m-3] """
        return self.grid[idx].get_layer_density()
    
    def get_snow_densities(self):
        """ Returns the snow layer density profile [kg m-3] (z) """
        return [self.grid[idx].get_layer_density() for idx in range(self.get_number_snow_layers())]

    def get_density(self):
        """ Returns the layer density profile [kg m-3] (z) """
        return [self.grid[idx].get_layer_density() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_liquid_water_content(self, idx):
        """ Returns the layer liquid water content of node idx [-] """
        return self.grid[idx].get_layer_liquid_water_content()

    def get_liquid_water_content(self):
        """ Returns the layer liquid water content profile [-] (z) """
        return [self.grid[idx].get_layer_liquid_water_content() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_ice_fraction(self, idx):
        """ Returns the layer ice fraction of node idx [-] """
        return self.grid[idx].get_layer_ice_fraction()

    def get_ice_fraction(self):
        """ Returns the layer ice fraction profile [-] (z) """
        return [self.grid[idx].get_layer_ice_fraction() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_irreducible_water_content(self, idx):
        """ Returns the layer irreducible water content of node idx [-] """
        return self.grid[idx].get_layer_irreducible_water_content()

    def get_irreducible_water_content(self):
        """ Returns the layer irreducible water content profile [-] (z) """
        return [self.grid[idx].get_layer_irreducible_water_content() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_cold_content(self, idx):
        """ Returns the layer cold content of node idx [J m-2] """
        return self.grid[idx].get_layer_cold_content()

    def get_cold_content(self):
        """ Returns the layer cold content profile [J m-2] (z) """
        return [self.grid[idx].get_layer_cold_content() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_porosity(self, idx):
        """ Returns the layer porosity of node idx [-] """
        return self.grid[idx].get_layer_porosity()

    def get_porosity(self):
        """ Returns the layer porosity profile [-] (z) """
        return [self.grid[idx].get_layer_porosity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_thermal_conductivity(self, idx):
        """ Returns the layer thermal conductivity of node idx [W m-1 K-1] """
        return self.grid[idx].get_layer_thermal_conductivity()

    def get_thermal_conductivity(self):
        """ Returns the layer thermal conductivity profile [W m-1 K-1] (z) """
        return [self.grid[idx].get_layer_thermal_conductivity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_thermal_diffusivity(self, idx):
        """ Returns the layer thermal diffusivity of node idx [m2 s-1] """
        return self.grid[idx].get_layer_thermal_diffusivity()

    def get_thermal_diffusivity(self):
        """ Returns the layer thermal diffusivity profile [m2 s-1] (z) """
        return [self.grid[idx].get_layer_thermal_diffusivity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #
    
    def get_node_refreeze(self, idx):
        """ Returns the layer refreezing of node idx [m w.e.] """
        return self.grid[idx].get_layer_refreeze()

    def get_refreeze(self):
        """ Returns the layer refreezing profile [m w.e.] (z) """
        return [self.grid[idx].get_layer_refreeze() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #
    
    def get_firn_node_refreeze(self, idx):
        """ Returns the firn layer refreezing of node idx [m w.e.] """
        return self.grid[idx].get_firn_layer_refreeze()    
    
    def get_firn_refreeze(self):
        """ Returns the firn layer refreezing profile [m w.e.] (z) """
        return [self.grid[idx].get_firn_layer_refreeze() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_depth(self):
        """ Returns the layer depth profile [m] (z) """
        depth = np.full(len(np.asarray(self.get_height())),np.nan)
        depth[0]  = 0.5 * self.get_node_height(0)
        depth[1:] = np.cumsum(np.asarray(self.get_height()))[:-1] + (0.5 * np.asarray(self.get_height()))[1:]        
        return depth

    # ---------------------------------------------- #

    def get_total_snowheight(self, verbose=False):
        """ Returns the total height of snow layers in the subsurface grid [m] """
        snowheights = [self.grid[idx].get_layer_height() for idx in range(self.number_nodes) if self.get_node_density(idx) < snow_ice_threshold]
        return np.sum(np.array(snowheights))

    def get_total_height(self, verbose=False):
        """ Returns the total height of the subsurface grid [m] """
        total = [self.get_node_height(idx) for idx in range(self.number_nodes)]
        return np.sum(np.array(total))

    # ---------------------------------------------- #

    def get_number_snow_layers(self):
        """ Returns the number of snow layers in the subsurface grid [n] """
        nlayers = [1 for idx in range(self.number_nodes) if self.get_node_density(idx)<snow_ice_threshold]
        return int(np.sum(np.array(nlayers)))

    def get_number_layers(self):
        """ Returns the number of layers in the subsurface grid [n] (z)"""
        return (self.number_nodes)
    
    # ---------------------------------------------- #

    def get_node_hydro_year(self, idx):
        """ Returns the layer hydrological year of node idx [yyyy] """
        return self.grid[idx].get_layer_hydro_year()
    
    def get_hydro_year(self):
        """ Returns the layer hydrological year profile [yyyy] (z) """
        return [self.grid[idx].get_layer_hydro_year() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_grain_size(self, idx):
        """ Returns the layer snow grain_size of node idx [mm] """
        return self.grid[idx].get_layer_grain_size()
    
    def get_grain_size(self):
        """ Returns the layer snow grain_sizes profile [mm] (z) """
        return [self.grid[idx].get_layer_grain_size() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_saturation(self, idx):
        """ Returns the layer water saturation of node idx [-] """
        return self.grid[idx].get_layer_saturation()
    
    def get_saturation(self):
        """ Returns the layer water saturation profile [-] (z) """
        return [self.grid[idx].get_layer_saturation() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_hydraulic_conductivity(self, idx):
        """ Returns the layer hydraulic_conductivity of node idx [m s-1] """
        return self.grid[idx].get_layer_hydraulic_conductivity()
    
    def get_hydraulic_conductivity(self):
        """ Returns the layer hydraulic_conductivity profile [m s-1] (z) """
        return [self.grid[idx].get_layer_hydraulic_conductivity() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_hydraulic_head(self, idx):
        """ Returns the layer hydraulic_head of node idx [m] """
        return self.grid[idx].get_layer_hydraulic_head()
    
    def get_hydraulic_head(self):
        """ Returns the layer hydraulic_head profile [m] (z) """
        return [self.grid[idx].get_layer_hydraulic_head() for idx in range(self.number_nodes)]

    # ================================================================================================== #