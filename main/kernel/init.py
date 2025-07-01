import numpy as np
from constants import *
from config import *
from main.kernel.grid import *

# =================== #
# Initialise Snowpack
# =================== #

def init_snowpack():
	
    layer_heights = []
    layer_densities = []
    layer_T = []
    layer_liquid_water = []

    # Snow / firn layers     
    if (initial_snowheight > 0.0):
        nlayers = int(initial_snowheight / initial_snow_layer_heights)
        dT = (initial_temperature_top-initial_temperature_bottom)/(initial_snowheight+initial_glacier_height)
        if nlayers == 0:
            layer_heights = np.array([initial_snowheight])
            layer_densities = np.array([initial_top_density_snowpack])
            layer_T = np.array([initial_temperature_top])
            layer_liquid_water = np.array([0.0])
        elif nlayers > 0:
            drho = (initial_top_density_snowpack-initial_bottom_density_snowpack)/initial_snowheight
            layer_heights = np.ones(nlayers) * (initial_snowheight/nlayers)
            layer_densities = np.array([initial_top_density_snowpack-drho*(initial_snowheight/nlayers)*i for i in range(1,nlayers+1)])
            layer_T = np.array([initial_temperature_top-dT*(initial_snowheight/nlayers)*i for i in range(1,nlayers+1)])
            layer_liquid_water = np.zeros(nlayers)
	    
        # Glacier layers
        nlayers = int(initial_glacier_height/initial_glacier_layer_heights)
        layer_heights = np.append(layer_heights, np.ones(nlayers)*initial_glacier_layer_heights)
        layer_densities = np.append(layer_densities, np.ones(nlayers)*ice_density)
        layer_T = np.append(layer_T, [layer_T[-1]-dT*initial_glacier_layer_heights*i for i in range(1,nlayers+1)])
        layer_liquid_water = np.append(layer_liquid_water, np.zeros(nlayers))
    
    # Glacier only
    else:
        nlayers = int(initial_glacier_height/initial_glacier_layer_heights)
        dT = (initial_temperature_top - initial_temperature_bottom)/initial_glacier_height
        layer_heights = np.ones(nlayers)*initial_glacier_layer_heights
        layer_densities = np.ones(nlayers)*ice_density
        layer_T = np.array([initial_temperature_top-dT*initial_glacier_layer_heights*i for i in range(1,nlayers+1)])
        layer_liquid_water = np.zeros(nlayers)

	# Initialise GRID
    GRID = Grid(np.array(layer_heights, dtype=np.float64), np.array(layer_densities, dtype=np.float64), 
                np.array(layer_T, dtype=np.float64), np.array(layer_liquid_water, dtype=np.float64),
                None, None, None, None, None)
    
    return GRID