"""
    ==================================================================

                        FRICOSIPY CONSTANTS FILE

        This file contains physical constants for calculations 
        within the model's physical processes. These values should 
        not be changed / altered.

    ================================================================== 
"""

# ================== #
# PHYSICAL CONSTANTS 
# ================== #

# Latent Heat:
latent_heat_melting = 3.34e5                    # Latent heat for melting [J kg-1]
latent_heat_vaporisation = 2.5e6                # Latent heat for vaporisation [J kg-1]
latent_heat_sublimation = 2.834e6               # Latent heat for sublimation [J kg-1]

# Specific Heat:
specific_heat_air = 1004.67                     # Specific heat of air [J kg-1 K-1]
specific_heat_water = 4217.                     # Specific heat of water [J Kg-1 K-1]
specific_heat_ice = 2050.                       # Specific heat of ice [J Kg-1 K-1]

# Density:
air_density = 1.1                               # Density of air [kg m-3]
water_density = 1000.                           # Density of water [kg m-3]
ice_density = 917.                              # Density of ice [kg m-3]

# Thermal Conductivity:
conductivity_air = 0.024                        # Thermal conductivity air [W m-1 K-1]
conductivity_water = 0.55                       # Thermal conductivity water [W m-1 K-1]
conductivity_ice = 2.22                         # Thermal conductivity ice [W m-1 K-1]

# Other:
g = 9.81                                        # Gravitational acceleration [m s-1]
M = 0.02896968                                  # Molar mass of Earth's air [kg mol-1]
R = 8.31432                                     # Universal gas constant [J mol-1 kg-1]
Atm_Pressure = 101500                           # Reference air pressure [Pa]
R_watervapour = 462.0                           # Specific gas constant water vapour [J kg-1 K-1]
R_dryair = 287.0                                # Specific gas constant dry air [J kg-1 K-1]
optical_depth = 1.6                             # Optical thickness/depth empirical constant
exp_aerosol = 0.97                              # Aerosol transmissivity exponent
zero_temperature = 273.16                       # Zero degrees [K]
sigma = 5.67e-8                                 # Stefan-Boltzmann constant [W m-2 K-4]