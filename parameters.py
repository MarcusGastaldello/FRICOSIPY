"""
    ==================================================================

                FRICOSIPY PARAMETERS & PARAMETERISATIONS FILE

        This file enables the user to modify the parameterisations
        of the model's physical processes and their associated
        paramaters as well as the simulation's initial conditions. 

    ==================================================================
"""

# ======================= #
# MODEL PARAMETERISATIONS 
# ======================= #

snow_density_method = 'constant'                  # Options: ['Vionnet12','constant']
albedo_method = 'Oerlemans98'                     # Options: ['Oerlemans98','Bougamont05','measured']
densification_method = 'Boone02'                  # Options: ['Boone02','Ligtenberg11','disabled']
penetrating_method = 'Bintanja95'                 # Options: ['Bintanja95','disabled']
roughness_method = 'Moelg12'                      # Options: ['Moelg12','constant']
saturation_vapour_pressure_method = 'Sonntag90'   # Options: ['Sonntag90']
thermal_conductivity_method = 'Calonne19'         # Options: ['bulk', 'empirical','Sturm97','Calonne19']
specific_heat_method = 'Yen81'                    # Options: ['bulk','Yen81']
preferential_percolation_method = 'disabled'      # Options: ['Marchenko17','disabled']
surface_temperature_method = 'Newton'             # Options: ['L-BFGS-B','SLSQP','Newton'] [slowest <--> fastest]
snow_metamorphism_method = 'Katsushima09'         # Options: ['Katsushima09','disabled']

# ================ #
# MODEL PARAMETERS 
# ================ #

# General Model Parameters:
dt = 3600                                       # Simulation time step [s] (minimum: 3600 s / hour)
max_depth = 50                                  # Maximum simulation depth [m]
max_layers = 500                                # Maximum number of subsurface layers               

# Meteorological Input Parameters:
station_altitude = 2680.0                       # Altitude of meteorological station [m a.s.l.]
z = 2.0                                         # Meteorological data measurement height [m] (typically 2m)
air_temperature_lapse_rate = -0.006             # Air temperature lapse rate [K m-1] (default = -0.006)
precipitation_lapse_rate = 0.0002               # Precipitation lapse rate [% m-1] (default = 0.0002)
precipitation_multiplier = 1.0                  # Scaling factor for adjusting precipitation data in meteorlogical forcing [-]
minimum_snowfall = 0.00001                      # Minimum snowfall per time step in m which is added as new snow [m]

# Physical Processes Parameters:
albedo_fresh_snow = 0.85                        # Albedo of fresh snow [-] (default = 0.85)
albedo_firn = 0.52                              # Albedo of firn [-] (default = 0.52)
albedo_ice = 0.30                               # Albedo of ice [-] (default = 0.30)
albedo_characteristic_snow_depth = 3.0          # Characteristic scale for snow depth [cm]
cloud_transmissivity_coeff_alpha = 0.233        # Cloud transmissivity coefficient alpha [-]
cloud_transmissivity_coeff_beta = 0.415         # Cloud transmissivity coefficient beta [-]
cloud_emissivity = 0.96                         # Emissivity of clouds [-] (default = 0.96)
LW_emission_constant = 0.42                     # Constant in the longwave emission formula [-] (default = 0.42)
subsurface_interpolation_depth_1 = 0.06         # First depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m] (default = 0.06)
subsurface_interpolation_depth_2 = 0.10         # Second depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m] (default = 0.10)
basal_heat_flux = 35                            # Basal / Geothermal heat flux [mW m-2] (default = 35)
pore_close_off_density = 830.0                  # Pore close-off density [kg m-3] (default = 830)
snow_ice_threshold = 900.0                      # Snow-ice density threshold [kg m-3] (default = 900)
surface_emission_coeff = 1.0                    # Surface emission coefficient for snow/ice [-] (default = 1.00)
firn_temperature_depth = 20.0                   # Depth at which firn temperature is measured [m]
grain_size_fresh_snow = 0.1                     # Grain size [mm] (default = 0.1)

# Parameterisation choice specifc:
preferential_percolation_depth = 3.0            # (Marchenko17) Charachteristic preferential percolation depth [m]
extinction_coeff_snow = 17.1                    # (Bintanja89) Extinction coefficient for snow [m-1]
extinction_coeff_ice = 2.5                      # (Bintanja89) Extinction coefficient for ice [m-1]
albedo_decay_timescale_wet = 10                 # (Bougamont05) Albedo decay timescale (melting surface) [days]
albedo_decay_timescale_dry = 30                 # (Bougamont05) Albedo decay timescale (dry snow surface) [days]
albedo_decay_timescale_dry_adjustment = 14      # (Bougamont05) Albedo dry snow decay timescale increase at negative temperatures [day K-1]
albedo_decay_timescale_threshold = 263.17       # (Bougamont05) Albedo temperature threshold for dry snow decay timescale increase [K]
albedo_decay_timescale = 22                     # (Oerlemans98) Albedo decay timescale (constant) [days]
surface_roughness_fresh_snow = 0.24             # (Moelg12) Surface roughness length for fresh snow [mm]
surface_roughness_ice = 1.7                     # (Moelg12) Surface roughness length for ice [mm]
surface_roughness_firn = 4.0                    # (Moelg12) Surface roughness length for aged snow [mm]
surface_roughness_timescale = 0.0026            # (Moelg12) Roughness length timescale [hours]
constant_fresh_snow_density = 250.              # (Constant - snow_density_method) Constant density of freshly fallen snow [kg m-3]
constant_surface_roughness = 0.001              # (Constant - surface_roughness_method) Surface roughness constant [m]
temperature_interpolation_depth_1 = 10          # (Ligtenberg11) First depth for temperature interpolation which is used for calculation of average subsurface layer temperature [m]
temperature_interpolation_depth_2 = 20          # (Ligtenberg11) Second depth for temperature interpolation which is used for calculation of average subsurface layer temperature [m]

# ============================ #
# SUBSURFACE REMESHING OPTIONS 
# ============================ #

minimum_snow_layer_height = 0.0005              # Minimum layer height [m]
maximum_simulation_layer_height = 0.10          # Maximum height of fine layers [m]
maximum_coarse_layer_height = 0.3               # Maximum height of coarse layers [m]
coarse_layer_threshold = 21.                    # Threshold depth at which fine near surface layers are merged into coarser deep layers [m]

# ================== #
# INITIAL CONDITIONS
# ================== #

initial_snowheight = 2.00                       # Initial snowheight [m]
initial_snow_layer_heights = 0.10               # Initial thickness of snow layers [m]
initial_snow_grain_size = 0.10                  # Initial snow grain size [mm]
initial_ice_grain_size = 5.0                    # Initial ice grain size [mm]
initial_glacier_height = 50.0                   # Initial glacier height (without snowlayers) [m]
initial_glacier_layer_heights = 1.0             # Initial thickness of glacier ice layers [m]
initial_upper_snowpack_density = 250.0          # Top density for initial snowpack [kg m-3]
initial_lower_snowpack_density = 275.0          # Bottom density for initial snowpack [kg m-3]
initial_upper_temperature = 270.16              # Upper boundary condition for initial temperature profile [K]
initial_lower_temperature = 273.16              # Lower boundary condition for initial temperature profile [K] 
