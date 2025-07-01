"""
 This is the FRICOSIPY simulation configuration file.
 Please make your changes here.
"""

# ================= #
# SIMULATION PERIOD 
# ================= #

# Date Range:
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

# Output File:
output_netcdf = 'Colle_Gnifetti_CURRENT.nc'

# Output Timestamps:
output_timestamps = 'Output_Timestamps_3H_2002-23.csv'

# ======================= #
# SPATIAL EXTENT / SUBSET 
# ======================= #

# Reduce Spatial Extent
subset = True

[x_min, x_max, y_min, y_max] = [2633810, 2633830, 1086580, 1086600] # Colle Gnifetti Sadde Point

# ================= #
# OUTPUT VARIABLES:
# ================= #    

# 3-D Output Variables:
meteorological_variables = ['AIR_TEMPERATURE','AIR_PRESSURE','RELATIVE_HUMIDITY','WIND_SPEED','FRACTIONAL_CLOUD_COVER']
surface_energy_fluxes  =   ['SHORTWAVE','LONGWAVE','SENSIBLE','LATENT','GROUND','RAIN_FLUX','MELT_ENERGY']
surface_mass_fluxes =      ['RAIN','SNOWFALL','EVAPORATION','SUBLIMATION','CONDENSATION','DEPOSITION','SURFACE_MELT','SMB']
subsurface_mass_fluxes =   ['REFREEZE','SUBSURFACE_MELT','RUNOFF','MB']
other =                    ['SNOW_HEIGHT','TOTAL_HEIGHT','SURFACE_TEMPERATURE','SURFACE_ALBEDO','N_LAYERS','FIRN_TEMPERATURE','FIRN_TEMPERATURE_CHANGE','FIRN_FACIE']

# 4-D Output Variables:
full_field = True                                               
subsurface_variables =   ['DEPTH','HEIGHT','DENSITY','TEMPERATURE','WATER_CONTENT','COLD_CONTENT','POROSITY','ICE_FRACTION','IRREDUCIBLE_WATER','REFREEZE','HYDRO_YEAR']

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