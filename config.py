"""
 This is the FRICOSIPY simulation configuration file.
 Please make your changes here.
"""

# ================= #
# SIMULATION PERIOD 
# ================= #

# Full 85 Year Simulation:
time_start   = '1939-01-01T00:00'
time_end     = '2023-12-31T23:00'

# Model Spin-up
model_spin_up = True
spin_up_end  = '2002-12-31T23:00'

# =================== #
# FILENAMES AND PATHS 
# =================== #

# Filepaths:
data_path = '../Data/'

# Input Files:
static_netcdf = 'Static_Colle_Gnifetti_20m.nc'
meteo_netcdf = 'Meteo_Colle_Gnifetti_1H_1939-23.nc'
illumination_netcdf = 'Illumination_Colle_Gnifetti_20m.nc'

# Output Files:
output_netcdf = 'Colle_Gnifetti.nc'
output_timestamps = 'Output_Timestamps_3H_2002-23.csv'

# ======================= #
# SPATIAL EXTENT / SUBSET 
# ======================= #

# Reduce Spatial Extent
subset = True

# ============== #
# COLLE GNIFETTI 
# ============== #

#[x_min, x_max, y_min, y_max] = [2633050, 2634150, 1085600, 1086780] # Colle Gnifetti 20m  Resolution / Validation / Points:
#[x_min, x_max, y_min, y_max] = [2633050, 2634150, 1085580, 1086780] # Colle Gnifetti 100m Resolution:
#[x_min, x_max, y_min, y_max] = [2633650, 2633670, 1086700, 1086720] # Zumsteinspitze Slope [ZS]: 
[x_min, x_max, y_min, y_max] = [2633810, 2633830, 1086580, 1086600] # Sadde Point [SP]: 
#[x_min, x_max, y_min, y_max] = [2633910, 2633930, 1086360, 1086380] # Signalkupper Slope [SK]: 

# ========== #
# MONTE ROSA 
# ========== #

#[x_min, x_max, y_min, y_max] = [2631625, 2634200, 1084400, 1086825] # Monte Rosa 25m Resolution:

# ============ #
# PLAINE MORTE 
# ============ #

#[x_min, x_max, y_min, y_max] = [2603100, 2608300, 1135700, 1138300] # Plaine Morte 100m Resolution:

# ================= #
# OUTPUT VARIABLES:
# ================= #    

# 3-D Output Variables:
surface_energy_fluxes  = ['SHORTWAVE','LONGWAVE','SENSIBLE','LATENT','GROUND','RAIN_FLUX','MELT_ENERGY']
surface_mass_fluxes =    ['RAIN','SNOWFALL','EVAPORATION','SUBLIMATION','CONDENSATION','DEPOSITION','SURFACE_MELT','SMB']
subsurface_mass_fluxes = ['REFREEZE','SUBSURFACE_MELT','RUNOFF','MB']
other =                  ['SNOW_HEIGHT','TOTAL_HEIGHT','SURF_TEMP','ALBEDO','N_LAYERS','FIRN_TEMPERATURE','FIRN_TEMPERATURE_CHANGE']
firn_temperature_depth = 20.

# 4-D Output Variables:
full_field = True                                               
subsurface_variables =   ['DEPTH','HEIGHT','DENSITY','TEMPERATURE','WATER_CONTENT','COLD_CONTENT','POROSITY','ICE_FRACTION','IRREDUCIBLE_WATER','REFREEZE','YEAR']   

# ================= #
# PARALLELIZATION 
# ================= #
workers = 1                                                # number of workers, if local cluster is used
local_port = 8786                                           # port for local cluster

# ================ #
# OUTPUT PRECISION
# ================ #

precision = 'single'                                        # either 'half' (16bit), 'single' (32bit) or 'double' (64bit)

# ============================ #
# COMPRESSION of Output NetCDF
# ============================ #
compression_level = 2                                       # Choose value between 1 and 9 (highest compression)
                                                            # Recommendation: choose 1, 2 or 3 (higher not worthwhile, because of needed time for writing output)                                    