"""
    ==================================================================

                    FRICOSIPY CONFIGURATION (CONFIG) FILE

        This file enables the user to configure their simulation by 
        selecting the input files (Static, Meteo & Illumination),
        simulation time range and output variables. 

    ================================================================== 
"""

# =================== #
# FILENAMES AND PATHS 
# =================== #

# Filepaths:
data_path = './data/'            # ('./data' current directory | '../data' parent directory)

# Input Files:
static_netcdf = '<static_file>.nc'
meteo_netcdf = '<meteo_file>.nc'
illumination_netcdf = '<illumination_file>.nc'

# Output File:
output_netcdf = '<output_file>.nc'

# ================= #
# SIMULATION PERIOD 
# ================= #

# Date Range:
time_start   = '2000-01-01T00:00' # Datetime (yyyy-mm-ddThh:mm)
time_end     = '2024-12-31T23:00' # Datetime (yyyy-mm-ddThh:mm)

# ========================== #
# OUTPUT REPORTING FREQUENCY 
# ========================== #

# Model Spin-up
model_spin_up = False              # Output variables are not aggregated during an initialisation / spin-up phase.
initial_timestamp  = None          # (Datetime (yyyy-mm-ddThh:mm) , if unused - 'None')

# Output Timestamps:
reduced_output = False             # Only report output variables on user-defined output timestamps.
output_timestamps = None           # CSV file with desired output timestamps (if unused - 'None').

# ======================= #
# SPATIAL EXTENT / SUBSET 
# ======================= #

# Grid Co-ordinate Reference System (CRS)
grid_crs = 'EPSG:2056'            # EPSG:xxxx (eg. EPSG:2056 - Metric Swiss CH1903+/LV95)

# Reduce Spatial Extent
spatial_subset = False            # Reduce the spatial extent of the static and illumination files to a single point or smaller computational area.
[x_min, x_max, y_min, y_max] = [2604300, 2604400, 1136500, 1136600] # (if unused - 'None')

# ================= #
# OUTPUT VARIABLES:
# ================= #    

# 3-D Output Variables:
meteorological_variables = ['AIR_TEMPERATURE','AIR_PRESSURE','RELATIVE_HUMIDITY','WIND_SPEED','FRACTIONAL_CLOUD_COVER']
surface_energy_fluxes  =   ['SHORTWAVE','LONGWAVE','SENSIBLE','LATENT','GROUND','RAIN_FLUX','MELT_ENERGY']
surface_mass_fluxes =      ['RAIN','SNOWFALL','EVAPORATION','SUBLIMATION','CONDENSATION','DEPOSITION','SURFACE_MELT','SURFACE_MASS_BALANCE']
subsurface_mass_fluxes =   ['REFREEZE','SUBSURFACE_MELT','RUNOFF','MASS_BALANCE']
other =                    ['SNOW_HEIGHT','SNOW_WATER_EQUIVALENT','TOTAL_HEIGHT','SURFACE_TEMPERATURE','SURFACE_ALBEDO','N_LAYERS','FIRN_TEMPERATURE','FIRN_TEMPERATURE_CHANGE','FIRN_FACIE']

# 4-D Output Variables:
full_field = False                                              
subsurface_variables =     ['DEPTH','HEIGHT','DENSITY','TEMPERATURE','WATER_CONTENT','COLD_CONTENT','POROSITY','ICE_FRACTION','IRREDUCIBLE_WATER','REFREEZE','HYDRO_YEAR','GRAIN_SIZE']

# ========================== #
# SIMULATION PARALLELIZATION 
# ========================== #

workers = 1                       # Number of processers/workers to simulatenously simulate grid nodes (Note: RAM/memory is shared by the number of processors selected)
local_port = 8786                 # port for local cluster

# ======================== #
# OUTPUT DATASET PRECISION
# ======================== #

precision = 'single'              # either 'half' (16bit), 'single' (32bit) or 'double' (64bit)

# ============================ #
# COMPRESSION of OUTPUT NetCDF
# ============================ #

compression_level = 2             # Choose value between 1 and 9 (highest compression)
                                  # Recommendation: choose 1, 2 or 3 (higher not worthwhile, because of needed time for writing output)
