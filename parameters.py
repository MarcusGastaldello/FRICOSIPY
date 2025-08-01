
# ======================= #
# MODEL PARAMETERISATIONS 
# ======================= #

snow_density_method = 'constant'                  # Options: ['Vionnet12','constant']
turbulent_fluxes_method = 'Essery04'   	          # Options: ['Essery04','Default']
stability_correction = 'Ri'                       # Options: ['Ri','MO']
albedo_method = 'Oerlemans98'                     # Options: ['Oerlemans98','Bougamont05','measured']
densification_method = 'Boone02'                  # Options: ['Boone02','Ligtenberg11','disabled']
penetrating_method = 'Bintanja95'                 # Options: ['Bintanja95','disabled']
roughness_method = 'Moelg12'                      # Options: ['Moelg12','constant']
saturation_water_vapour_method = 'Sonntag90'      # Options: ['Sonntag90']
thermal_conductivity_method = 'Calonne19'         # Options: ['bulk', 'empirical','Sturm97','Calonne19']
specific_heat_method = 'Yen81'                    # Options: ['bulk','Yen81']
preferential_percolation_method = 'Marchenko17'   # Options: ['Marchenko17','disabled']
sfc_temperature_method = 'Newton'             	  # Options: ['L-BFGS-B','SLSQP','Newton']

# ================ #
# MODEL PARAMETERS 
# ================ #

# General Model Parameters:
dt = 3600                                       # Simulation time step [s] (minimum: 3600 / hour)
max_depth = 50                                  # Maximum simulation depth [m]
max_layers = 500                                # Maximum number of subsurface layers               

# Meteorological Input Parameters:
station_altitude = 4560.0                       # Altitude of meteorological station [m a.s.l.]
z = 2.0                                         # Meteorological data measurement height [m] (typically 2m)
air_temperature_lapse_rate = -0.006             # Air temperature lapse rate [K m-1]
precipitation_lapse_rate = 0.002                # Precipitation lapse rate [% m-1]
precipitation_multiplier = 1.0                  # Scaling factor for adjusting precipitation data in meteorlogical forcing [-]
minimum_snowfall = 0.00001                      # Minimum snowfall per time step in m which is added as new snow [m]

# Physical Processes Parameters:
albedo_fresh_snow = 0.81                        # Albedo of fresh snow [-]
albedo_firn = 0.52                              # Albedo of firn [-]
albedo_ice = 0.3                                # Albedo of ice [-]
albedo_mod_snow_depth = 3                       # Effect of snow depth on albedo [cm]
alpha = 0.233                                   # (Greuell97) Cloud transmissivity coefficient alpha [-]
beta = 0.415                                    # (Greuell97) Cloud transmissivity coefficient beta [-]
e_clouds = 0.960                                # Emissivity of clouds [-]
LW_emission_constant = 0.420                    # Constant in the longwave emission formula [-]
zlt1 = 0.06                                     # First depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m]
zlt2 = 0.10                                     # Second depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m]
basal_heat_flux = 35                            # Basal / Geothermal heat flux [mW m^(-2)]
snow_ice_threshold = 900.0                      # Pore close of density [kg m^(-3)]
surface_emission_coeff = 1.0                    # Surface emission coefficient for snow/ice [-]
firn_temperature_depth = 20.0                   # Depth at which firn temperature is measured [m]    

# Parameterisation choice specifc:
z_lim = 3.0                                     # (Marchenko17) Preferential percolation depth [m]
extinction_coeff_snow = 17.1                    # (Bintanja89) Extinction coefficient for snow [m-1]
t_star_wet = 10                                 # (Bougamont05) Albedo decay timescale (melting surface) [days]
t_star_dry = 30                                 # (Bougamont05) Albedo decay timescale (dry snow surface) [days]
t_star_K = 5                                    # (Bougamont05) Albedo dry snow decay timescale increase at negative temperatures [day K-1]
t_star_cutoff = 263.17                          # (Bougamont05) Albedo temperature threshold for dry snow decay timescale increase [K]
albedo_mod_snow_aging = 22                      # (Oerlemans98) Albedo decay timescale (constant) [days]
roughness_fresh_snow = 0.24                     # (Moelg12) Surface roughness length for fresh snow [mm]
roughness_ice = 1.7                             # (Moelg12) Surface roughness length for ice [mm]
roughness_firn = 4.0                            # (Moelg12) Surface roughness length for aged snow [mm]
aging_factor_roughness = 0.0026                 # (Moelg12) Roughness length timescale [hours]
constant_density = 275.                         # (Constant - snow_density_method) Constant density of freshly fallen snow [kg m-3]
roughness_constant = 0.001                      # (Constant - surface_roughness_method) Surface roughness constant [m]
z1 = 10                                         # (Ligtenberg11) First depth for temperature interpolation which is used for calculation of average subsurface layer temperature [m]
z2 = 20                                         # (Ligtenberg11) Second depth for temperature interpolation which is used for calculation of average subsurface layer temperature [m]

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

initial_snowheight = 50.                        # Initial snowheight [m]
initial_snow_layer_heights = 0.10               # Initial thickness of snow layers [m]
initial_glacier_height = 0.0                    # Initial glacier height (without snowlayers) [m]
initial_glacier_layer_heights = 1.0             # Initial thickness of glacier ice layers [m]
initial_top_density_snowpack = 250.0            # Top density for initial snowpack [kg m-3]
initial_bottom_density_snowpack = 700.0         # Bottom density for initial snowpack [kg m-3]
initial_temperature_top = 258.80                # Upper boundary condition for initial temperature profile [K]
initial_temperature_bottom = 259.60             # Lower boundary condition for initial temperature profile [K] 
