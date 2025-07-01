import numpy as np
from constants import *
from parameters import *
from config import *
from main.kernel.node import *
import os
from collections import OrderedDict
from numba import types, typed, intp, float64, optional
from numba.experimental import jitclass

node_type = Node.class_type.instance_type
spec = OrderedDict()
spec['layer_heights'] = float64[:]
spec['layer_densities'] = float64[:]
spec['layer_temperatures'] = float64[:]
spec['layer_liquid_water_content'] = float64[:]
spec['layer_ice_fraction'] = optional(float64[:])
spec['number_nodes'] = intp
spec['new_snow_height'] = float64
spec['new_snow_timestamp'] = float64
spec['old_snow_timestamp'] = float64
spec['fresh_snow_timestamp'] = float64
spec['grid'] = types.ListType(node_type)

# =========== #
# Grid Class:
# =========== #

@jitclass(spec)
class Grid:

    def __init__(self, layer_heights, layer_densities, layer_temperatures, layer_liquid_water_content, layer_ice_fraction=None,
        new_snow_height=None, new_snow_timestamp=None, old_snow_timestamp=None, fresh_snow_timestamp=None):
        """ The Grid-class controls the numerical mesh. 
        
        The grid consists of a list of nodes (layers) that store the information 
        of individual layers. The class provides various setter/getter functions
        to add, read, overwrite, merge, split, update or re-mesh the layers. 

        Parameters
        ----------
            layer_heights : float
                Height of the snowpack layers [:math:`m`]
            layer_densities : float
                Snow density of the snowpack layers [:math:`kg~m^{-3}`]
            layer_temperatures : float
                Temperatures of the layers [:math:`K`]
            layer_liquid_water_content : float
                Liquid water content of the layers [:math:`m~w.e.`]

        Returns
        -------
            Node : :py:class:`cosipy.cpkernel.grid` object

        """
        # Set class variables
        self.layer_heights = layer_heights
        self.layer_densities = layer_densities
        self.layer_temperatures = layer_temperatures
        self.layer_liquid_water_content = layer_liquid_water_content
        self.layer_ice_fraction = layer_ice_fraction

        # Number of total nodes
        self.number_nodes = len(layer_heights)

        # Track the fresh snow layer (new_snow_height, new_snow_timestamp) as well as the old
        # snow layer age (old_snow_timestamp)
        if (new_snow_height is not None) and (new_snow_timestamp is not None) and \
           (old_snow_timestamp is not None):
            self.new_snow_height = new_snow_height         # meter snow accumulation
            self.new_snow_timestamp = new_snow_timestamp   # seconds since snowfall
            self.old_snow_timestamp = old_snow_timestamp   # snow age below fresh snow layer
            self.fresh_snow_timestamp = fresh_snow_timestamp # seconds since snowfall (not overidden in case of uppermost layer melt)
        else:
	    #TO DO: pick better initialization values
            self.new_snow_height = 0.0      
            self.new_snow_timestamp = 0.0   
            self.old_snow_timestamp = 0.0
            self.fresh_snow_timestamp = 0.0

        # Do the grid initialization
        self.grid = typed.List.empty_list(node_type)

        self.init_grid()

    # -------------------------------------------------------------------------------------------------- #

    # =============== #
    # Initialise GRID
    # =============== #

    def init_grid(self):
        """ Initialize the grid with according to the input data """
        # Fill the list with node instances and fill it with user defined data
        for idxNode in range(self.number_nodes):
            layer_IF = None
            if self.layer_ice_fraction is not None:
                layer_IF = self.layer_ice_fraction[idxNode]
            self.grid.append(Node(self.layer_heights[idxNode], self.layer_densities[idxNode],
                self.layer_temperatures[idxNode], self.layer_liquid_water_content[idxNode], layer_IF))

    # -------------------------------------------------------------------------------------------------- #

    # ==================== #
    # Add Fresh Snow Layer
    # ==================== #

    def add_fresh_snow(self, height, density, temperature, liquid_water_content):
        """ Adds a fresh snow layer (node) at the beginning of the node list (upper layer) 

        Parameters
        ----------
            height : float
                Height of the layer [:math:`m`]
            density : float
                Density of the layer [:math:`kg~m^{-3}`]
            temperature : float
                Temperature of the layer [:math:`K`]
            liquid_water_content : float
                Liquid water content of the layer [:math:`m~w.e.`]
        """
	
        # Add new node
        self.grid.insert(0, Node(height, density, temperature, liquid_water_content, None))

        # Increase node counter
        self.number_nodes += 1

        # Set the fresh snow properties for albedo calculation (height and timestamp)
        self.set_fresh_snow_props(height)

    # -------------------------------------------------------------------------------------------------- #

    # =================== #
    # Remove Layer / Node
    # =================== #

    def remove_node(self, idx = None):
        """ Removes a layer (node) from the grid (node list). 
        
        Parameters
        ----------
            idx : int
                Index of the node to be removed. If no index is provided the first
                node is beeing removed.

        """

        # Remove node from list when there is at least one node
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

    # -------------------------------------------------------------------------------------------------- #

    # ==================== #
    # Merge Layers / Nodes
    # ==================== #

    def merge_nodes(self, idx):
        """ Merges two subsequent nodes. 
        
        This function merges the two nodes at location idx and idx+1. The node at idx is updated
        with the new properties (height, liquid water content, ice fraction, temperature), while the node
        at idx+1 is deleted after merging.

        Parameters
        ----------
            idx : int
                Index of the node to be removed. If no index is provided the first
                node is beeing removed.
        
        """ 

        # New layer height by adding up the height of the two layers
        new_height = self.get_node_height(idx) + self.get_node_height(idx + 1)

        # Update liquid water
        new_liquid_water_content = (self.get_node_liquid_water_content(idx) * self.get_node_height(idx) + \
                                    self.get_node_liquid_water_content(idx+1) * self.get_node_height(idx + 1)) / new_height

        # Update ice fraction
        new_ice_fraction = ((self.get_node_ice_fraction(idx) * self.get_node_height(idx) + \
                            self.get_node_ice_fraction(idx+1) * self.get_node_height(idx + 1)) / new_height)

        # New air porosity
        new_air_porosity = 1 - new_liquid_water_content - new_ice_fraction

        if abs(1 - new_ice_fraction - new_air_porosity - new_liquid_water_content) > 1e-8:
            print('Merging is not mass consistent',(new_ice_fraction + new_air_porosity + new_liquid_water_content))

        # Calculate new temperature
        new_temperature = (self.get_node_height(idx)/new_height)*self.get_node_temperature(idx) + \
                            (self.get_node_height(idx+1)/new_height)*self.get_node_temperature(idx+1)
        
        # Update refrozen quantity
        new_refreeze = self.get_node_refreeze(idx) + self.get_node_refreeze(idx + 1)
        new_firn_refreeze = self.get_firn_node_refreeze(idx) + self.get_firn_node_refreeze(idx + 1)
        
        # Update node properties
        self.update_node(idx, new_height, new_temperature, new_ice_fraction, new_liquid_water_content, new_refreeze, new_firn_refreeze)
        
        # Remove the second layer
        self.remove_node([idx+1])

    # -------------------------------------------------------------------------------------------------- #

    # ====================== #
    # Remesh Subsurface Grid
    # ====================== #    

    def update_grid(self):
        """ Re-meshes the layers (numerical grid)."""
                     
        self.lagrangian_profile()

        # ---------------------------------------------------------------------------------------------- #

    def lagrangian_profile(self):

        # Merge uppermost layer with the second layer unless it exceeds the maximum layer height or they are from different hydrological years
        if (self.get_number_layers() >= 2):  
            if ((self.get_node_height(0) + self.get_node_height(1) <= maximum_simulation_layer_height) and (self.get_node_hydro_year(0) == self.get_node_hydro_year(1))):
                self.merge_nodes(0)
        
        # Merge into coarser layers if a layer goes beyond the region of interest:
        idx = np.searchsorted(self.get_depth(), coarse_layer_threshold, side="right")
        if (idx + 1 <= (self.get_number_layers() - 1)): 
            if (self.get_node_height(idx) + self.get_node_height(idx + 1) <= maximum_coarse_layer_height):
                self.merge_nodes(idx)

        # If last layer depth exceeds the desired subsurface measurement depth, remove it
        idx = self.get_number_layers() - 1
        if (self.get_depth()[idx] > max_depth):
            self.remove_node([idx])
        
    # -------------------------------------------------------------------------------------------------- #

    # ====================== #
    # Remesh Subsurface Grid
    # ====================== #

    def update_node(self, idx, height, temperature, ice_fraction, liquid_water_content, refreeze, firn_refreeze):
        """ Update properties of a specific node.

        This function updates the properties height, temperature, ice_fraction, liquid water
        content, refreeze and firn refreeze of a layer. 

        Parameters
        ----------
            idx : int
                Index of the layer to be updated.
            layer_heights : float
                New height of the snowpack layers [:math:`m`]
            layer_temperatures : float
                New temperatures of the layers [:math:`K`]
            ice_fraction : float
                New ice fraction of the layer [:math:`-`]
            layer_liquid_water_content : float
                New liquid water content of the layers [:math:`m~w.e.`]
            layer_refreeze :
                New refrozen content of the layers [:math:`m~w.e.`]
            firn layer_refreeze :
                New refrozen content of the firn layers [:math:`m~w.e.`]
        
        """
        self.set_node_height(idx,height)
        self.set_node_temperature(idx,temperature)
        self.set_node_ice_fraction(idx,ice_fraction)
        self.set_node_liquid_water_content(idx,liquid_water_content)
        self.set_node_refreeze(idx,refreeze)
        self.set_firn_node_refreeze(idx,firn_refreeze)

    # -------------------------------------------------------------------------------------------------- #

    # ================= #
    # Check GRID Layers
    # ================= #

    def check(self, name):
        """ Function checks whether temperature and layer heights are within the valid range """
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
        if np.max(self.get_height()) > 1.0:
            print(name)
            print('Layer height exceeds 1.0 m')
            print(self.get_height())
            print(self.get_density())

    # -------------------------------------------------------------------------------------------------- #

    # ================= #
    # Remove Layer Mass
    # ================= #

    def remove_mass(self, mass, idx = 0):
        """ Removes mass from a layer.
              
        Parameters
        ----------
            meass : float
                Snow water equivalent of mass to be removed [:math:`m~w.e.`]
            idx : int
                Index of the layer. 
        """

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

        # Keep track of the fresh snow layer
        if (idx == 0):
            self.set_fresh_snow_props_height(self.new_snow_height - mass)

    # ================================================================================================== #

    #======================== #
    # Snow Property Functions
    #======================== #

    def set_fresh_snow_props(self, height):
        """ Keeps track of the new snowheight.
        
        Parameters
        ----------
            height : float
                Height of the fresh snow layer [:math:`m`].
        """
        self.new_snow_height = height
        # Keep track of the old snow age
        self.old_snow_timestamp = self.new_snow_timestamp
        # Set the timestamp to zero
        self.new_snow_timestamp = 0
        self.fresh_snow_timestamp = 0

    def set_fresh_snow_props_to_old_props(self):
        """ Sets the timestamp of the fresh snow properties back to the timestamp of the underlying snow layer.
        
        The function is used internally to keep track of the albedo properties of the first snow
        layer.
        """
        self.new_snow_timestamp = self.old_snow_timestamp

    def set_fresh_snow_props_update_time(self, seconds):
        """ Update timestamp of snow props.

        Parameters
        ----------
            height : float
                Height of the fresh snow layer [:math:`m`].
            seconds : float
                seconds without snowfall
                [:math:`s`].
        """
        self.old_snow_timestamp = self.old_snow_timestamp + seconds
        self.new_snow_timestamp = self.new_snow_timestamp + seconds
        self.fresh_snow_timestamp = self.fresh_snow_timestamp + seconds

    def set_fresh_snow_props_height(self, height):
        """ Updates the fresh snow layer height property.
        
        The function is used internally to keep track of the albedo properties oir the first snow
        layer.
        """
        self.new_snow_height = height
	
    def get_fresh_snow_props(self):
        """ Returns the properties of the first snow layer.

        The function is used internally to keep track of the albedo properties oir the first snow
        layer.
        """
        return self.new_snow_height, self.new_snow_timestamp, self.old_snow_timestamp

    # ================================================================================================== #

    # ================================= #
    # Set Functions for Layer Variables
    # ================================= #

    def set_node_temperature(self, idx, temperature):
        """ Sets the temperature of layer (node) at location idx."""
        self.grid[idx].set_layer_temperature(temperature)

    def set_temperature(self, temperature):
        """ Sets the temperature of layer (node) at location idx."""
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_temperature(temperature[idx])

        # ---------------------------------------------- #

    def set_node_height(self, idx, height):
        """ Set height of node idx """
        self.grid[idx].set_layer_height(height)

    def set_height(self, height):
        """ Set height of profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_height(height[idx])

    # ---------------------------------------------- #

    def set_node_liquid_water_content(self, idx, liquid_water_content):
        """ Set liquid water content of node idx """
        self.grid[idx].set_layer_liquid_water_content(liquid_water_content)

    def set_liquid_water_content(self, liquid_water_content):
        """ Set the liquid water content profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_liquid_water_content(liquid_water_content[idx])

    # ---------------------------------------------- #

    def set_node_ice_fraction(self, idx, ice_fraction):
        """ Set liquid ice_fraction of node idx """
        self.grid[idx].set_layer_ice_fraction(ice_fraction)

    def set_ice_fraction(self, ice_fraction):
        """ Set the ice_fraction profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_ice_fraction(ice_fraction[idx])

    # ---------------------------------------------- #

    def set_node_refreeze(self, idx, refreeze):
        """ Set refreezing of node idx """
        self.grid[idx].set_layer_refreeze(refreeze)

    def set_refreeze(self, refreeze):
        """ Set the refreezing profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_refreeze(refreeze[idx])

    def set_firn_node_refreeze(self, idx, firn_refreeze):
        """ Set the refreezing of firn node idx """
        self.grid[idx].set_firn_layer_refreeze(firn_refreeze)

    def set_firn_refreeze(self, firn_refreeze):
        """ Set the refreezing profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_firn_layer_refreeze(firn_refreeze[idx])

    # ---------------------------------------------- #     

    def set_node_hydro_year(self, idx, hydro_year):
        """ Set accumulation hydrological year of node idx """
        self.grid[idx].set_layer_hydro_year(hydro_year)

    def set_hydro_year(self, hydro_year):
        """ Set accumulation hydrological years of profile """
        for idx in range(self.number_nodes):
            self.grid[idx].set_layer_hydro_year(hydro_year[idx])

    # ================================================================================================== #

    # ================================= #
    # Get Functions for Layer Variables
    # ================================= #

    def get_temperature(self):
        """ Returns the temperature profile """
        return [self.grid[idx].get_layer_temperature() for idx in range(self.number_nodes)]

    def get_node_temperature(self, idx):
        """ Returns temperature of node idx """
        return self.grid[idx].get_layer_temperature()

    # ---------------------------------------------- #

    def get_specific_heat(self):
        """ Returns the specific heat (air+water+ice) profile """
        return [self.grid[idx].get_layer_specific_heat() for idx in range(self.number_nodes)]

    def get_node_specific_heat(self, idx):
        """ Returns specific heat (air+water+ice) of node idx """
        return self.grid[idx].get_layer_specific_heat()

    # ---------------------------------------------- #

    def get_height(self):
        """ Returns the heights of the layers """
        return [self.grid[idx].get_layer_height() for idx in range(self.number_nodes)]

    def get_snow_heights(self):
        """ Returns the heights of the snow layers """
        return [self.grid[idx].get_layer_height() for idx in range(self.get_number_snow_layers())]

    def get_ice_heights(self):
        """ Returns the heights of the ice layers """
        return [self.grid[idx].get_layer_height() for idx in range(self.number_nodes) if (self.get_node_density(idx)>=snow_ice_threshold)]

    def get_node_height(self, idx):
        """ Returns layer height of node idx """
        return self.grid[idx].get_layer_height()
    
    # ---------------------------------------------- #

    def get_node_density(self, idx):
        """ Returns density of node idx """
        return self.grid[idx].get_layer_density()

    def get_density(self):
        """ Returns the rho profile """
        return [self.grid[idx].get_layer_density() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_liquid_water_content(self, idx):
        """ Returns density of node idx """
        return self.grid[idx].get_layer_liquid_water_content()

    def get_liquid_water_content(self):
        """ Returns the rho profile """
        return [self.grid[idx].get_layer_liquid_water_content() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_ice_fraction(self, idx):
        """ Returns ice fraction of node idx """
        return self.grid[idx].get_layer_ice_fraction()

    def get_ice_fraction(self):
        """ Returns the liquid water profile """
        return [self.grid[idx].get_layer_ice_fraction() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_irreducible_water_content(self, idx):
        """ Returns irreducible water content of node idx """
        return self.grid[idx].get_layer_irreducible_water_content()

    def get_irreducible_water_content(self):
        """ Returns the irreducible water content profile """
        return [self.grid[idx].get_layer_irreducible_water_content() for idx in range(self.number_nodes)]

    # ---------------------------------------------- #

    def get_node_cold_content(self, idx):
        """ Returns cold content of node idx """
        return self.grid[idx].get_layer_cold_content()

    def get_cold_content(self):
        """ Returns the cold content profile """
        return [self.grid[idx].get_layer_cold_content() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_porosity(self, idx):
        """ Returns porosity of node idx """
        return self.grid[idx].get_layer_porosity()

    def get_porosity(self):
        """ Returns the porosity profile """
        return [self.grid[idx].get_layer_porosity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_thermal_conductivity(self, idx):
        """ Returns the thermal conductivity of node idx """
        return self.grid[idx].get_layer_thermal_conductivity()

    def get_thermal_conductivity(self):
        """ Returns the thermal conductivity profile """
        return [self.grid[idx].get_layer_thermal_conductivity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_node_thermal_diffusivity(self, idx):
        """ Returns the thermal diffusivity of node idx """
        return self.grid[idx].get_layer_thermal_diffusivity()

    def get_thermal_diffusivity(self):
        """ Returns the thermal diffusivity profile """
        return [self.grid[idx].get_layer_thermal_diffusivity() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #
    
    def get_node_refreeze(self, idx):
        """ Returns refreezing of node idx """
        return self.grid[idx].get_layer_refreeze()

    def get_refreeze(self):
        """ Returns the refreezing profile """
        return [self.grid[idx].get_layer_refreeze() for idx in range(self.number_nodes)]
    
    def get_firn_node_refreeze(self, idx):
        """ Returns refreezing of firn node idx """
        return self.grid[idx].get_firn_layer_refreeze()    
    
    def get_firn_refreeze(self):
        """ Returns the firn refreezing profile """
        return [self.grid[idx].get_firn_layer_refreeze() for idx in range(self.number_nodes)]
    
    # ---------------------------------------------- #

    def get_depth(self):
        """ Returns depth profile """
        depth = np.full(len(np.asarray(self.get_height())),np.nan)
        depth[0]  = 0.5 * self.get_node_height(0)
        depth[1:] = np.cumsum(np.asarray(self.get_height()))[:-1] + (0.5 * np.asarray(self.get_height()))[1:]        
        return depth

    # ---------------------------------------------- #

    def get_total_snowheight(self, verbose=False):
        """ Get the total snowheight (density<snow_ice_threshold)"""
        snowheights = [self.grid[idx].get_layer_height() for idx in range(self.number_nodes) if self.get_node_density(idx)<snow_ice_threshold]
        return np.sum(np.array(snowheights))	#numba needs to be able to determine type of list contents 

    def get_total_height(self, verbose=False):
        """ Get the total domain height """
        total = [self.get_node_height(idx) for idx in range(self.number_nodes)]
        return np.sum(np.array(total))

    # ---------------------------------------------- #

    def get_number_snow_layers(self):
        """ Get the number of snow layers (density<snow_ice_threshold)"""
        nlayers = [1 for idx in range(self.number_nodes) if self.get_node_density(idx)<snow_ice_threshold]
        return int(np.sum(np.array(nlayers)))

    def get_number_layers(self):
        """ Get the number of layers"""
        return (self.number_nodes)
    
        # ---------------------------------------------- #

    def get_node_hydro_year(self, idx):
        """ Returns accumulation hydrological year of node idx """
        return self.grid[idx].get_layer_hydro_year()
    
    def get_hydro_year(self):
        """ Returns accumulation hydrological year profile """
        return [self.grid[idx].get_layer_hydro_year() for idx in range(self.number_nodes)]

    # ================================================================================================== #

    # =============================== #
    # Auxillary Information Functions
    # =============================== #

    def info(self):
        """ Print some information on grid """

        print("******************************")
        print("Number of nodes:",self.number_nodes)
        print("******************************")

        tmp = 0
        for i in range(self.number_nodes):
            tmp = tmp + self.get_node_height(i)

        print("Grid consists of",self.number_nodes,"nodes")
        print("Total domain depth is",tmp,"m")

    # ---------------------------------------------- #

    def grid_info(self, n=-999):
        """ The function prints the state of the snowpack
            Args:
                n   : number of nodes to plot (from top)
        """
        if (n==-999):
            n = self.number_nodes

        print("Node no., Layer height [m], Temperature [K], Density [kg m^-3], \
               LWC [-], LW [m], CC [J m^-2], Porosity [-], Refreezing [m w.e.], \
	       Irreducible water content [-]")

        for i in range(n):
            print(i, self.get_node_height(i), self.get_node_temperature(i), self.get_node_density(i), 
                     self.get_node_liquid_water_content(i), self.get_node_cold_content(i),
                     self.get_node_porosity(i), self.get_node_refreeze(i), self.get_node_irreducible_water_content(i))

    # ---------------------------------------------- #

    def grid_info_screen(self, n=-999):
        """ The function prints the state of the snowpack
            Args:
                n   : number of nodes to plot (from top)
        """
        if (n==-999):
            n = self.number_nodes

        print("Node no., Layer height [m], Temperature [K], Density [kg m^-3], LWC [-], \
               Retention [-], CC [J m^-2], Porosity [-], Refreezing [m w.e.]")

        for i in range(n):
            print(i, self.get_node_height(i), self.get_node_temperature(i),
                  self.get_node_density(i), self.get_node_liquid_water_content(i), 
                  self.get_node_irreducible_water_content(i), self.get_node_cold_content(i),
                  self.get_node_porosity(i), self.get_node_refreeze(i))

    # ---------------------------------------------- #

    def grid_check(self, level=1):
        """ The function checks the grid
            Args:
                n   : number of nodes to plot (from top)
        """
        #if level == 1:
        #    self.check_layer_property(self.get_height(), 'thickness', 1.01, -0.001)
        #    self.check_layer_property(self.get_temperature(), 'temperature', 273.2, 100.0)
        #    self.check_layer_property(self.get_density(), 'density', 918, 100)
        #    self.check_layer_property(self.get_liquid_water_content(), 'LWC', 1.0, 0.0)
        #    #self.check_layer_property(self.get_cold_content(), 'CC', 1000, -10**8)
        #    self.check_layer_property(self.get_porosity(), 'Porosity', 0.8, -0.00001)
        #    self.check_layer_property(self.get_refreeze(), 'Refreezing', 0.5, 0.0)



    def check_layer_property(self, property, name, maximum, minimum, n=-999, level=1):
        if np.nanmax(property) > maximum or np.nanmin(property) < minimum:
            print(str.capitalize(name),'max',np.nanmax(property),'min',np.nanmin(property))
            os._exit()
    
    # ================================================================================================== #
