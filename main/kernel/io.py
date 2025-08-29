"""
    ==================================================================

                    FRICOSIPY INPUT / OUTPUT (IO) FILE

        This file reads the model input datasets (Static, Meteo and
        Illumination) and creates the model output RESULT dataset
        contained within the IO Python Class.

    ==================================================================
"""

import os
import xarray as xr
import numpy as np
import pandas as pd
import dask.array as da
import rioxarray 
from constants import *
from parameters import *
from config import * 
import sys

# ========================== #
# Input / Output (IO) Class:
# ========================== #

class IOClass:

    def __init__(self, STATIC = None, METEO = None, ILLUMINATION = None):
        """ Initialises the Input/Output (IO) Class """

        # Read variable list from file¨:
        self.meteorological_variables = meteorological_variables
        self.surface_energy_fluxes = surface_energy_fluxes
        self.surface_mass_fluxes = surface_mass_fluxes
        self.subsurface_mass_fluxes = subsurface_mass_fluxes
        self.other = other
        self.subsurface_variables = subsurface_variables

        # Initialise input datasets:
        self.METEO = METEO
        self.STATIC = STATIC
        self.ILLUMINATION = ILLUMINATION

    # =================================================================================================
        
    # =============================== #
    # Loads the Input STATIC Dataset:
    # =============================== #
    def load_static_file(self):
        """ Returns the STATIC Xarray dataset """

        # Open input static dataset 
        self.STATIC = xr.open_dataset(os.path.join(data_path,'static',static_netcdf))

        # Select spatial extent from config.py
        if spatial_subset == True:
            self.STATIC = self.STATIC.sel(y = slice(y_min,y_max), x = slice(x_min,x_max))
        
        # Grid Dimensions
        self.ny = self.STATIC.sizes['y']
        self.nx = self.STATIC.sizes['x']

        # Print information about the spatial grid:
        if self.ny > 1:
            grid_resolution = str(abs(self.STATIC.y.values[1] - self.STATIC.y.values[0])) + ' m'
        elif self.nx > 1:
            grid_resolution = str(abs(self.STATIC.x.values[1] - self.STATIC.x.values[0])) + ' m'
        else:
            grid_resolution = 'N/A (Point simulation)'

        if spatial_subset == True:
            print('\t Spatial Grid Extent: [X:',x_min,'-',x_max,'| Y: ',y_min,'-',y_max,']. Spatial Resolution:',grid_resolution)
        else:
            print('\t Spatial Grid Extent: [X:',str(self.STATIC.x.values[0]),'-',str(self.STATIC.x.values[-1]),'| Y:',str(self.STATIC.y.values[0]),'-',str(self.STATIC.y.values[-1]),']. Spatial Resolution:',grid_resolution)        
        print('\t Glacier Grid Nodes: %s' %(np.nansum(self.STATIC.MASK >= 1)))

        return self.STATIC
    
    # =================================================================================================

    # ============================== #
    # Loads the Input METEO Dataset:
    # ============================== #

    def load_meteo_file(self):
        """ Returns the METEO Xarray dataset """

        # Open input meteorological dataset
        self.METEO = xr.open_dataset(os.path.join(data_path,'meteo',meteo_netcdf))
        self.METEO['time'] = np.sort(self.METEO['time'].values)

        # Print meteorological information:
        start_interval=str(self.METEO.time.values[0])[0:16]
        end_interval = str(self.METEO.time.values[-1])[0:16]
        time_steps = str(self.METEO.sizes['time'])
        print('\t Simulation Temporal Range from %s until %s. Simulation Timesteps: %s ' % (start_interval, end_interval, time_steps))      

        # Check for datetime errors in config file:
        if (np.asarray(time_start, dtype = np.datetime64) < self.METEO.time.values[0]) or (np.asarray(time_end, dtype = np.datetime64) > self.METEO.time.values[-1]):
            raise ValueError('Error: Selected simulation start and end dates are outside the temporal range of the input meteorological file.')

        if model_spin_up == True:
            if not (time_start < initial_timestamp < time_end):
                raise ValueError('Error: Initial timestamp is not contained within the temporal range of the input meteorological file.')

        if reduced_output == True:
            if  (np.asarray(time_start, dtype = np.datetime64) > pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64)).any() or \
                (pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64) > np.asarray(time_end, dtype = np.datetime64)).any():
                raise ValueError('Error: Output timestamps are outside the temporal range of the input meteorological file.')

            if model_spin_up == True:
                if  (np.asarray(initial_timestamp, dtype = np.datetime64) > pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64)).any() or \
                    (pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64) > np.asarray(time_end, dtype = np.datetime64)).any():
                    raise ValueError('Error: Output timestamps are outside the temporal range of the input meteorological file and the model spin-up.')

        # Select Temporal Range
        self.METEO = self.METEO.sel(time=slice(time_start, time_end))

        return self.METEO
    
    # =================================================================================================

    # ===================================== #
    # Loads the Input ILLUMINATION Dataset:
    # ===================================== #

    def load_illumination_file(self):
        """ Returns the ILLUMINATION Xarray dataset """

        # Open input illumination dataset
        self.ILLUMINATION = xr.open_dataset(os.path.join(data_path,'illumination',illumination_netcdf))

        # Select spatial extent from config.py
        if spatial_subset == True:
            self.ILLUMINATION = self.ILLUMINATION.sel(y = slice(y_min,y_max), x = slice(x_min,x_max))

        print('\t ==============================================================\n')

        return self.ILLUMINATION
    
    # =================================================================================================

    # ================================== #
    # Creates the RESULT Xarray Dataset:
    # ================================== #

    def create_result_file(self):
        """ Returns the RESULT Xarray dataset """
        self.init_result_dataset()
        return self.RESULT

    # ====================================== #
    # Initialises the RESULT Xarray Dataset:
    # ====================================== #

    def init_result_dataset(self):
        """ Initialise the RESULT Xarray dataset """

        self.RESULT = xr.Dataset()

        # Spatial coordinates
        self.RESULT.coords['y'] = self.STATIC.coords['y']
        self.RESULT.coords['x'] = self.STATIC.coords['x'] 

        # Temporal range   
        if reduced_output == True:

            # Output variables are reported on user-defined output timestamps:
            self.RESULT.coords['time'] = pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64).flatten()

            # Final simulation timestamp must be included in the output timestamps to prevent an error:
            if pd.to_datetime(time_end).to_numpy()  not in self.RESULT.coords['time']:
                self.RESULT.coords['time'] = np.append(self.RESULT.coords['time'],np.asarray(time_end, dtype = np.datetime64))

        else:
            if model_spin_up == True:

                # Output variables are reported on all simulation timestamps after the model has initialised / user-defined model spin-up has completed.
                self.RESULT.coords['time'] = self.METEO.sel(time=slice(initial_timestamp, time_end)).coords['time']
            else:
                
                # Output variables are reported on all simulation timestamps
                self.RESULT.coords['time'] = self.METEO.coords['time'] 

        # Output File Temporal Dimension
        self.nt = self.RESULT.sizes['time']

        # ===================================== #
        # Assign Attributes to the NETCDF File:
        # ===================================== #

        # Global attributes from config.py
        self.RESULT.attrs['Compression_level'] = compression_level
        self.RESULT.attrs['Full_field'] = str(full_field)

        # Global attributes from parameters.py

        # Model Parameterisations:
        self.RESULT.attrs['Snow_density_method'] = snow_density_method
        self.RESULT.attrs['Turbulent_fluxes_method'] = turbulent_fluxes_method
        self.RESULT.attrs['Stability_correction'] = stability_correction
        self.RESULT.attrs['Albedo_method'] = albedo_method
        self.RESULT.attrs['Densification_method'] = densification_method
        self.RESULT.attrs['Penetrating_method'] = penetrating_method
        self.RESULT.attrs['Roughness_method'] = roughness_method
        self.RESULT.attrs['Saturation_water_vapour_method'] = saturation_water_vapour_method
        self.RESULT.attrs['Thermal_conductivity_method'] = thermal_conductivity_method
        self.RESULT.attrs['Specific_heat_method'] = specific_heat_method
        self.RESULT.attrs['Water_percolation_method'] = preferential_percolation_method
        self.RESULT.attrs['Sfc_temperature_method'] = sfc_temperature_method
        self.RESULT.attrs['Snow_metamorphism_method'] = snow_metamorphism_method

        # Initial Conditions:
        self.RESULT.attrs['Initial_snowheight'] = initial_snowheight
        self.RESULT.attrs['Initial_snow_layer_heights'] = initial_snow_layer_heights
        self.RESULT.attrs['Initial_grain_size'] = initial_snow_grain_size
        self.RESULT.attrs['Initial_grain_size'] = initial_ice_grain_size
        self.RESULT.attrs['Initial_glacier_height'] = initial_glacier_height
        self.RESULT.attrs['Initial_glacier_layer_heights'] = initial_glacier_layer_heights
        self.RESULT.attrs['Initial_upper_snowpack_density'] = initial_upper_snowpack_density
        self.RESULT.attrs['Initial_lower_snowpack_density'] = initial_lower_snowpack_density
        self.RESULT.attrs['Initial_lower_temperature'] = initial_lower_temperature
        self.RESULT.attrs['Initial_upper_temperature'] = initial_upper_temperature

        # Subsurface Remeshing Options:    
        self.RESULT.attrs['Max_layers'] = max_layers
        self.RESULT.attrs['Minimum_snow_layer_height'] = minimum_snow_layer_height
        self.RESULT.attrs['Maximum_simulation_layer_height'] = maximum_simulation_layer_height
        self.RESULT.attrs['Maximum_coarse_layer_height'] = maximum_coarse_layer_height
        self.RESULT.attrs['Coarse_layer_threshold'] = coarse_layer_threshold

        # Model Parameters (General):
        self.RESULT.attrs['Time_step_input_file_seconds'] = dt
        self.RESULT.attrs['Max_simulation_depth'] = max_depth
        self.RESULT.attrs['Station_altitude'] = station_altitude
        self.RESULT.attrs['Z_measurment_height'] = z
        self.RESULT.attrs['Albedo_fresh_snow'] = albedo_fresh_snow
        self.RESULT.attrs['Albedo_firn'] = albedo_firn
        self.RESULT.attrs['Albedo_ice'] = albedo_ice
        self.RESULT.attrs['Albedo_characteristic_snow_depth'] = albedo_characteristic_snow_depth
        self.RESULT.attrs['Cloud_transmissivity_coeff_alpha'] = cloud_transmissivity_coeff_alpha
        self.RESULT.attrs['Cloud_transmissivity_coeff_beta'] = cloud_transmissivity_coeff_beta
        self.RESULT.attrs['Clouds_emissivity_constant'] = cloud_emissivity
        self.RESULT.attrs['Longwave_emission_constant'] = LW_emission_constant
        self.RESULT.attrs['Subsurface_interpolation_depth_1'] = subsurface_interpolation_depth_1
        self.RESULT.attrs['Subsurface_interpolation_depth_1'] = subsurface_interpolation_depth_1
        self.RESULT.attrs['Basal_heat_flux'] = basal_heat_flux
        self.RESULT.attrs['Minimum_snowfall'] = minimum_snowfall
        self.RESULT.attrs['Snow_ice_threshold'] = snow_ice_threshold
        self.RESULT.attrs['Surface_emission_coeff'] = surface_emission_coeff

        # Model Parameters (Parameterisation-specific):
        if preferential_percolation_method == 'Marchenko17':
            self.RESULT.attrs['Characteristic_preferential_percolation_depth'] = preferential_percolation_depth
        if penetrating_method == 'Bintanja95':
            self.RESULT.attrs['Extinction_coeff_snow'] = extinction_coeff_snow
            self.RESULT.attrs['Extinction_coeff_ice'] = extinction_coeff_ice
        if albedo_method == 'Bougamont05':
            self.RESULT.attrs['Albedo_decay_timescale_wet_snow_surface'] = albedo_decay_timescale_wet
            self.RESULT.attrs['Albedo_decay_timescale_dry_snow_surface'] = albedo_decay_timescale_dry
            self.RESULT.attrs['Albedo_decay_timescale_adjustment'] = albedo_decay_timescale_dry_adjustment
            self.RESULT.attrs['Albedo_decay_timescale_threshold'] = albedo_decay_timescale_threshold
        elif albedo_method == 'Oerlemans98':
            self.RESULT.attrs['Albedo_mod_snow_aging'] = albedo_characteristic_snow_depth
        if roughness_method == 'Moelg12':
            self.RESULT.attrs['Surface_roughness_fresh_snow'] = surface_roughness_fresh_snow
            self.RESULT.attrs['Surface_roughness_ice'] = surface_roughness_ice
            self.RESULT.attrs['Surface_roughness_firn'] = surface_roughness_firn
            self.RESULT.attrs['Surface_roughness_timescale'] = surface_roughness_timescale
        elif roughness_method == 'constant':
            self.RESULT.attrs['Constant_fresh_snow_density'] = constant_fresh_snow_density
        if snow_density_method == 'constant':
            self.RESULT.attrs['Constant_surface_roughness'] = constant_surface_roughness
        if densification_method == 'Ligtenberg11':
            self.RESULT.attrs['Temperature_interpolation_depth_1'] = temperature_interpolation_depth_1
            self.RESULT.attrs['Temperature_interpolation_depth_2'] = temperature_interpolation_depth_2

        # Global attributes from constants.py

        # Physical Constants:
        self.RESULT.attrs['Latent_heat_melting'] = lat_heat_melting
        self.RESULT.attrs['Latent_heat_vaporize'] = lat_heat_vaporize
        self.RESULT.attrs['Latent_heat_sublimation'] = lat_heat_sublimation
        self.RESULT.attrs['Specific_heat_capacity_air'] = spec_heat_air
        self.RESULT.attrs['Specific_heat_capacity_water'] = spec_heat_water
        self.RESULT.attrs['Specific_heat_capacity_ice'] = spec_heat_ice
        self.RESULT.attrs['Thermal_conductivity_air'] = k_a
        self.RESULT.attrs['Thermal_conductivity_water'] = k_w
        self.RESULT.attrs['Thermal_conductivity_ice'] = k_i
        self.RESULT.attrs['Density_air'] = air_density
        self.RESULT.attrs['Density_water'] = water_density
        self.RESULT.attrs['Density_ice'] = ice_density
        self.RESULT.attrs['Gravitational_acceleration'] = g
        self.RESULT.attrs['M'] = M
        self.RESULT.attrs['Gas_constant'] = R
        self.RESULT.attrs['Atmouspheric_Pressure'] = Atm_Pressure
        self.RESULT.attrs['R_watervapour'] = R_watervapour
        self.RESULT.attrs['R_dryair'] = R_dryair
        self.RESULT.attrs['Optical_depth'] = optical_depth
        self.RESULT.attrs['exp_aerosol'] = exp_aerosol
        self.RESULT.attrs['Stefan-Boltzmann_constant'] = sigma
        self.RESULT.attrs['Zero_temperature'] = zero_temperature

        # ====================================== #
        # Add Static Variables to Result Dataset
        # ====================================== #

        # Variables given by the input dataset
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ELEVATION, 'ELEVATION', 'm', 'Elevation')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.MASK, 'MASK', 'boolean', 'Glacier mask')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.SLOPE, 'SLOPE', 'degrees', 'Terrain slope')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ASPECT, 'ASPECT', 'degrees', 'Aspect of slope')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.EASTING, 'EASTING', 'm', 'X Co-ordinate of Projection')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.NORTHING, 'NORTHING', 'm', 'X Co-ordinate of Projection')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.LONGITUDE, 'LONGITUDE', 'm', 'degrees')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.LATITUDE, 'LATITUDE', 'm', 'degrees')
        if 'BASAL' in list(self.STATIC.keys()):
            self.add_variable_along_northingeasting(self.RESULT, self.STATIC.BASAL, 'BASAL', 'mW m\u207b\xb2', 'Basal Heat Flux')
        if 'ACCUMULATION' in list(self.STATIC.keys()):
            self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ACCUMULATION, 'ACCUMULATION', 'm a\u207b\xb9', 'Annual Accumulation Climatology')
        if 'SUBLIMATION' in list(self.STATIC.keys()):
            self.add_variable_along_northingeasting(self.RESULT, self.STATIC.SUBLIMATION, 'SUBLIMATION', 'm a\u207b\xb9', 'Annual Sublimation Climatology')
        if 'THICKNESS' in list(self.STATIC.keys()):    
            self.add_variable_along_northingeasting(self.RESULT, self.STATIC.THICKNESS, 'THICKNESS', 'm', 'Glacier Thickness')

        # Convert to Dask arrays for efficient computation:
        self.RESULT = self.RESULT.chunk(chunks='auto')

        # ========================================= #
        # Assign Co-ordinate Reference System (CRS)
        # ========================================= #

        self.RESULT = self.RESULT.sortby(['time', 'x', 'y'])
        self.RESULT = self.RESULT.rio.write_crs(grid_crs)
            
        return self.RESULT
    
    # =================================================================================================
  
    # ==================== #
    # Global Result Arrays
    # ==================== #

    def create_global_result_arrays(self):
        """ Creates the global result arrays in the RESULT Xarray dataset """

        # Meteorological Variables (5):
        if ('AIR_TEMPERATURE' in self.meteorological_variables):
            self.AIR_TEMPERATURE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('AIR_PRESSURE' in self.meteorological_variables):
            self.AIR_PRESSURE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('RELATIVE_HUMIDITY' in self.meteorological_variables):
            self.RELATIVE_HUMIDITY = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('WIND_SPEED' in self.meteorological_variables):
            self.WIND_SPEED = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('FRACTIONAL_CLOUD_COVER' in self.meteorological_variables):
            self.FRACTIONAL_CLOUD_COVER = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)

        # Surface Energy Fluxes (7):
        if ('SHORTWAVE' in self.surface_energy_fluxes):
            self.SHORTWAVE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('LONGWAVE' in self.surface_energy_fluxes):
            self.LONGWAVE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SENSIBLE' in self.surface_energy_fluxes):
            self.SENSIBLE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('LATENT' in self.surface_energy_fluxes):
            self.LATENT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('GROUND' in self.surface_energy_fluxes):
            self.GROUND = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('RAIN_FLUX' in self.surface_energy_fluxes):
            self.RAIN_FLUX = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('MELT_ENERGY' in self.surface_energy_fluxes):
            self.MELT_ENERGY = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)

        # Surface Mass Fluxes (8):
        if ('RAIN' in self.surface_mass_fluxes):
            self.RAIN = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SNOWFALL' in self.surface_mass_fluxes):
            self.SNOWFALL = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('EVAPORATION' in self.surface_mass_fluxes):
            self.EVAPORATION = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SUBLIMATION' in self.surface_mass_fluxes):
            self.SUBLIMATION = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('CONDENSATION' in self.surface_mass_fluxes):
            self.CONDENSATION = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('DEPOSITION' in self.surface_mass_fluxes):
            self.DEPOSITION = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURFACE_MELT' in self.surface_mass_fluxes):
            self.SURFACE_MELT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURFACE_MASS_BALANCE' in self.surface_mass_fluxes):
            self.SURFACE_MASS_BALANCE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.REFREEZE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.SUBSURFACE_MELT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.RUNOFF = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('MASS_BALANCE' in self.subsurface_mass_fluxes):
            self.MASS_BALANCE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)

        # Other Information (9):
        if ('SNOW_HEIGHT' in self.other):
            self.SNOW_HEIGHT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SNOW_WATER_EQUIVALENT' in self.other):
            self.SNOW_WATER_EQUIVALENT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('TOTAL_HEIGHT' in self.other):
            self.TOTAL_HEIGHT = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURFACE_TEMPERATURE' in self.other):
            self.SURFACE_TEMPERATURE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURFACE_ALBEDO' in self.other):
            self.SURFACE_ALBEDO = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('N_LAYERS' in self.other):
            self.N_LAYERS = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('FIRN_TEMPERATURE' in self.other):
            self.FIRN_TEMPERATURE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.FIRN_TEMPERATURE_CHANGE = np.full((self.nt,self.ny,self.nx), np.nan, dtype = precision)
        if ('FIRN_FACIE' in self.other):
            self.FIRN_FACIE = np.zeros((self.nt,self.ny,self.nx), dtype = 'int32')

        # Subsurface Variables (12):
        if full_field:
            if ('DEPTH' in self.subsurface_variables):
                self.LAYER_DEPTH = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('HEIGHT' in self.subsurface_variables):
                self.LAYER_HEIGHT = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('DENSITY' in self.subsurface_variables):
                self.LAYER_DENSITY = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('TEMPERATURE' in self.subsurface_variables):
                self.LAYER_TEMPERATURE = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('WATER_CONTENT' in self.subsurface_variables):
                self.LAYER_WATER_CONTENT = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('COLD_CONTENT' in self.subsurface_variables):
                self.LAYER_COLD_CONTENT = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('POROSITY' in self.subsurface_variables):
                self.LAYER_POROSITY = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('ICE_FRACTION' in self.subsurface_variables):
                self.LAYER_ICE_FRACTION = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('IRREDUCIBLE_WATER' in self.subsurface_variables):
                self.LAYER_IRREDUCIBLE_WATER = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('REFREEZE' in self.subsurface_variables):
                self.LAYER_REFREEZE = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('HYDRO_YEAR' in self.subsurface_variables):
                self.LAYER_HYDRO_YEAR = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('GRAIN_SIZE' in self.subsurface_variables):
                self.LAYER_GRAIN_SIZE = np.full((self.nt,self.ny,self.nx,max_layers), np.nan, dtype = precision)

    
    # =================================================================================================

    # ================================================= #
    # Assign Local Node Results to Global Result Arrays
    # ================================================= #
    
    def copy_local_to_global(self,y,x,
        local_AIR_TEMPERATURE,local_AIR_PRESSURE,local_RELATIVE_HUMIDITY,local_WIND_SPEED,local_FRACTIONAL_CLOUD_COVER, \
        local_SHORTWAVE,local_LONGWAVE,local_SENSIBLE,local_LATENT,local_GROUND,local_RAIN_FLUX,local_MELT_ENERGY, \
        local_RAIN,local_SNOWFALL,local_EVAPORATION,local_SUBLIMATION,local_CONDENSATION,local_DEPOSITION,local_SURFACE_MELT,local_SURFACE_MASS_BALANCE, \
        local_REFREEZE,local_SUBSURFACE_MELT,local_RUNOFF,local_MASS_BALANCE, \
        local_SNOW_HEIGHT,local_SNOW_WATER_EQUIVALENT,local_TOTAL_HEIGHT,local_SURFACE_TEMPERATURE,local_SURFACE_ALBEDO,local_N_LAYERS,local_FIRN_TEMPERATURE,local_FIRN_TEMPERATURE_CHANGE,local_FIRN_FACIE, \
        local_LAYER_DEPTH,local_LAYER_HEIGHT,local_LAYER_DENSITY,local_LAYER_TEMPERATURE,local_LAYER_WATER_CONTENT,local_LAYER_COLD_CONTENT,local_LAYER_POROSITY,local_LAYER_ICE_FRACTION, \
        local_LAYER_IRREDUCIBLE_WATER,local_LAYER_REFREEZE,local_LAYER_HYDRO_YEAR,local_LAYER_GRAIN_SIZE):
        """ Fills the global result arrays with local variables from each node """

        # Meteorological Variables (5):
        if ('AIR_TEMPERATURE' in self.meteorological_variables):
            self.AIR_TEMPERATURE[:,y,x] = local_AIR_TEMPERATURE
        if ('AIR_PRESSURE' in self.meteorological_variables):
            self.AIR_PRESSURE[:,y,x] = local_AIR_PRESSURE
        if ('RELATIVE_HUMIDITY' in self.meteorological_variables):
            self.RELATIVE_HUMIDITY[:,y,x] = local_RELATIVE_HUMIDITY
        if ('WIND_SPEED' in self.meteorological_variables):
            self.WIND_SPEED[:,y,x] = local_WIND_SPEED
        if ('FRACTIONAL_CLOUD_COVER' in self.meteorological_variables):
            self.FRACTIONAL_CLOUD_COVER[:,y,x] = local_FRACTIONAL_CLOUD_COVER

        # Surface Energy Fluxes (7):
        if ('SHORTWAVE' in self.surface_energy_fluxes):
            self.SHORTWAVE[:,y,x] = local_SHORTWAVE
        if ('LONGWAVE' in self.surface_energy_fluxes):
            self.LONGWAVE[:,y,x] = local_LONGWAVE
        if ('SENSIBLE' in self.surface_energy_fluxes):
            self.SENSIBLE[:,y,x] = local_SENSIBLE
        if ('LATENT' in self.surface_energy_fluxes):
            self.LATENT[:,y,x] = local_LATENT 
        if ('GROUND' in self.surface_energy_fluxes):
            self.GROUND[:,y,x] = local_GROUND 
        if ('RAIN_FLUX' in self.surface_energy_fluxes):
            self.RAIN_FLUX[:,y,x] = local_RAIN_FLUX 
        if ('MELT_ENERGY' in self.surface_energy_fluxes):
            self.MELT_ENERGY[:,y,x] = local_MELT_ENERGY

        # Surface Mass Fluxes (8):
        if ('RAIN' in self.surface_mass_fluxes):
            self.RAIN[:,y,x] = local_RAIN
        if ('SNOWFALL' in self.surface_mass_fluxes):
            self.SNOWFALL[:,y,x] = local_SNOWFALL
        if ('EVAPORATION' in self.surface_mass_fluxes):
            self.EVAPORATION[:,y,x] = local_EVAPORATION
        if ('SUBLIMATION' in self.surface_mass_fluxes):
            self.SUBLIMATION[:,y,x] = local_SUBLIMATION
        if ('CONDENSATION' in self.surface_mass_fluxes):
            self.CONDENSATION[:,y,x] = local_CONDENSATION
        if ('DEPOSITION' in self.surface_mass_fluxes):
            self.DEPOSITION[:,y,x] = local_DEPOSITION
        if ('SURFACE_MELT' in self.surface_mass_fluxes):
            self.SURFACE_MELT[:,y,x] = local_SURFACE_MELT
        if ('SURFACE_MASS_BALANCE' in self.surface_mass_fluxes):
            self.SURFACE_MASS_BALANCE[:,y,x] = local_SURFACE_MASS_BALANCE

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.REFREEZE[:,y,x] = local_REFREEZE
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.SUBSURFACE_MELT[:,y,x] = local_SUBSURFACE_MELT
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.RUNOFF[:,y,x] = local_RUNOFF
        if ('MASS_BALANCE' in self.subsurface_mass_fluxes):
            self.MASS_BALANCE[:,y,x] = local_MASS_BALANCE         

        # Other Information (9):
        if ('SNOW_HEIGHT' in self.other):
            self.SNOW_HEIGHT[:,y,x] = local_SNOW_HEIGHT
        if ('SNOW_WATER_EQUIVALENT' in self.other):
            self.SNOW_WATER_EQUIVALENT[:,y,x] = local_SNOW_WATER_EQUIVALENT
        if ('TOTAL_HEIGHT' in self.other):
            self.TOTAL_HEIGHT[:,y,x] = local_TOTAL_HEIGHT
        if ('SURFACE_TEMPERATURE' in self.other):
            self.SURFACE_TEMPERATURE[:,y,x] = local_SURFACE_TEMPERATURE
        if ('SURFACE_ALBEDO' in self.other):
            self.SURFACE_ALBEDO[:,y,x] = local_SURFACE_ALBEDO
        if ('N_LAYERS' in self.other):
            self.N_LAYERS[:,y,x] = local_N_LAYERS
        if ('FIRN_TEMPERATURE' in self.other):
            self.FIRN_TEMPERATURE[:,y,x] = local_FIRN_TEMPERATURE
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.FIRN_TEMPERATURE_CHANGE[:,y,x] = local_FIRN_TEMPERATURE_CHANGE
        if ('FIRN_FACIE' in self.other):
            self.FIRN_FACIE[:,y,x] = local_FIRN_FACIE
        
        # Subsurface Variables (12):
        if full_field:
            if ('DEPTH' in self.subsurface_variables):
                self.LAYER_DEPTH[:,y,x,:] = local_LAYER_DEPTH
            if ('HEIGHT' in self.subsurface_variables):
                self.LAYER_HEIGHT[:,y,x,:] = local_LAYER_HEIGHT 
            if ('DENSITY' in self.subsurface_variables):
                self.LAYER_DENSITY[:,y,x,:] = local_LAYER_DENSITY 
            if ('TEMPERATURE' in self.subsurface_variables):
                self.LAYER_TEMPERATURE[:,y,x,:] = local_LAYER_TEMPERATURE
            if ('WATER_CONTENT' in self.subsurface_variables):
                self.LAYER_WATER_CONTENT[:,y,x,:] = local_LAYER_WATER_CONTENT 
            if ('COLD_CONTENT' in self.subsurface_variables):
                self.LAYER_COLD_CONTENT[:,y,x,:] = local_LAYER_COLD_CONTENT 
            if ('POROSITY' in self.subsurface_variables):
                self.LAYER_POROSITY[:,y,x,:] = local_LAYER_POROSITY 
            if ('ICE_FRACTION' in self.subsurface_variables):
                self.LAYER_ICE_FRACTION[:,y,x,:] = local_LAYER_ICE_FRACTION 
            if ('IRREDUCIBLE_WATER' in self.subsurface_variables):
                self.LAYER_IRREDUCIBLE_WATER[:,y,x,:] = local_LAYER_IRREDUCIBLE_WATER 
            if ('REFREEZE' in self.subsurface_variables):
                self.LAYER_REFREEZE[:,y,x,:] = local_LAYER_REFREEZE 
            if ('HYDRO_YEAR' in self.subsurface_variables):
                self.LAYER_HYDRO_YEAR[:,y,x,:] = local_LAYER_HYDRO_YEAR
            if ('GRAIN_SIZE' in self.subsurface_variables):
                self.LAYER_GRAIN_SIZE[:,y,x,:] = local_LAYER_GRAIN_SIZE

    # =================================================================================================

    # =================================== #
    # Write Results to Output NETCDF File
    # =================================== #

    def write_results_to_file(self):
        """ Writes the results into the RESULT Xarray dataset """

        # Meteorological Variables (5):
        if ('AIR_TEMPERATURE' in self.meteorological_variables):
            self.add_variable_along_northingeastingtime(self.RESULT, self.AIR_TEMPERATURE, 'AIR_TEMPERATURE', '°C', 'Air Temperature')
        if ('AIR_PRESSURE' in self.meteorological_variables):
            self.add_variable_along_northingeastingtime(self.RESULT, self.AIR_PRESSURE, 'AIR_PRESSURE', 'hPa', 'Air Pressure')
        if ('RELATIVE_HUMIDITY' in self.meteorological_variables):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RELATIVE_HUMIDITY, 'RELATIVE_HUMIDITY', '%', 'Relative Humidity')
        if ('WIND_SPEED' in self.meteorological_variables):
            self.add_variable_along_northingeastingtime(self.RESULT, self.WIND_SPEED, 'WIND_SPEED', 'm s\u207b\xb9', 'Wind Speed')
        if ('FRACTIONAL_CLOUD_COVER' in self.meteorological_variables):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FRACTIONAL_CLOUD_COVER, 'FRACTIONAL_CLOUD_COVER', '-', 'Fractional Cloud Cover')

        # Surface Energy Fluxes (7):
        if ('SHORTWAVE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SHORTWAVE, 'SHORTWAVE', 'W m\u207b\xb2', 'Net Shortwave Flux')
        if ('LONGWAVE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.LONGWAVE, 'LONGWAVE', 'W m\u207b\xb2', 'Net Longwave Flux')
        if ('SENSIBLE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SENSIBLE, 'SENSIBLE', 'W m\u207b\xb2', 'Net Sensible Flux')
        if ('LATENT' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.LATENT, 'LATENT', 'W m\u207b\xb2', 'Net Latent Flux')
        if ('GROUND' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.GROUND, 'GROUND', 'W m\u207b\xb2', 'Net Ground Flux')
        if ('RAIN_FLUX' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RAIN_FLUX, 'RAIN_FLUX', 'W m\u207b\xb2', 'Rain Heat Flux')
        if ('MELT_ENERGY' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.MELT_ENERGY, 'MELT_ENERGY', 'W m\u207b\xb2', 'Melt Flux')

        # Surface Mass Fluxes (8):
        if ('RAIN' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RAIN, 'RAIN', 'm w.e.', 'Rain')
        if ('SNOWFALL' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SNOWFALL, 'SNOWFALL', 'm w.e.', 'Snowfall')
        if ('EVAPORATION' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.EVAPORATION, 'EVAPORATION', 'm w.e.', 'Evaporation')
        if ('SUBLIMATION' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SUBLIMATION, 'SUBLIMATION', 'm w.e.', 'Sublimation')
        if ('CONDENSATION' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.CONDENSATION, 'CONDENSATION', 'm w.e.', 'Condensation')
        if ('DEPOSITION' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.DEPOSITION, 'DEPOSITION', 'm w.e.', 'Moisture Deposition')
        if ('SURFACE_MELT' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SURFACE_MELT, 'SURFACE_MELT', 'm w.e.', 'Surface Melt')
        if ('SURFACE_MASS_BALANCE' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SURFACE_MASS_BALANCE, 'SURFACE_MASS_BALANCE', 'm w.e.', 'Surface Mass Balance')

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.REFREEZE, 'REFREEZE', 'm w.e.', 'Refreezing')
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SUBSURFACE_MELT, 'SUBSURFACE_MELT', 'm w.e.', 'Subsurface Melt')
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RUNOFF, 'RUNOFF', 'm w.e.', 'Runoff')
        if ('MASS_BALANCE' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.MASS_BALANCE, 'MASS_BALANCE', 'm w.e.', 'Mass Balance')       

        # Other Information (9):
        if ('SNOW_HEIGHT' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SNOW_HEIGHT, 'SNOW_HEIGHT', 'm', 'Snow Height')
        if ('SNOW_WATER_EQUIVALENT' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SNOW_WATER_EQUIVALENT, 'SNOW_WATER_EQUIVALENT', 'm w.e.', 'Snow Water Equivalent')
        if ('TOTAL_HEIGHT' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.TOTAL_HEIGHT, 'TOTAL_HEIGHT', 'm', 'Total Height')
        if ('SURFACE_TEMPERATURE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SURFACE_TEMPERATURE, 'SURFACE_TEMPERATURE', '°C', 'Surface Temperature')
        if ('SURFACE_ALBEDO' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SURFACE_ALBEDO, 'SURFACE_ALBEDO', '-', 'Surface Albedo')
        if ('N_LAYERS' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.N_LAYERS, 'N_LAYERS', 'n', 'Number of Layers')
        if ('FIRN_TEMPERATURE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FIRN_TEMPERATURE, 'FIRN_TEMPERATURE', '°C', 'Firn Temperature at x m Depth')
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FIRN_TEMPERATURE_CHANGE, 'FIRN_TEMP_CHANGE', 'ΔC', 'Firn Warming at x m Depth')
        if ('FIRN_FACIE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FIRN_FACIE, 'FIRN_FACIE', '-', '1 : Recrystallization | 2 : Recrystallization-Infiltraion | 3 : Cold-Infilitration | 4 : Temperate')

        # Subsurface Variables (12):
        if full_field:
            if ('DEPTH' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_DEPTH, 'LAYER_DEPTH', 'm', 'Layer Depth')
            if ('HEIGHT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_HEIGHT, 'LAYER_HEIGHT', 'm', 'Layer Height') 
            if ('DENSITY' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_DENSITY, 'LAYER_DENSITY', 'kg m\u207b\xb3', 'Layer Density') 
            if ('TEMPERATURE' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_TEMPERATURE, 'LAYER_TEMPERATURE', '°C', 'Layer Temperature') 
            if ('WATER_CONTENT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_WATER_CONTENT, 'LAYER_WATER_CONTENT', '-', 'Layer Liquid Water Content') 
            if ('COLD_CONTENT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_COLD_CONTENT, 'LAYER_COLD_CONTENT', 'J m\u207b\xb2', 'Layer Cold Content') 
            if ('POROSITY' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_POROSITY, 'LAYER_POROSITY', '-', 'Layer Porosity') 
            if ('ICE_FRACTION' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_ICE_FRACTION, 'LAYER_ICE_FRACTION', '-', 'Layer Ice Fraction') 
            if ('IRREDUCIBLE_WATER' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_IRREDUCIBLE_WATER, 'LAYER_IRR_WATER', '-', 'Layer Irreducible Water') 
            if ('REFREEZE' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_REFREEZE, 'LAYER_REFREEZE', 'm w.e.', 'Layer Refreezing')   
            if ('HYDRO_YEAR' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_HYDRO_YEAR, 'LAYER_HYDRO_YEAR', 'yyyy', 'Layer Hydrological Year') 
            if ('GRAIN_SIZE' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_GRAIN_SIZE, 'LAYER_GRAIN_SIZE', 'mm', 'Layer Grain Size')                   

    # =================================================================================================

    # ======================= #
    # Retreive Result Dataset
    # ======================= #

    def get_result(self):
        """ Returns the RESULT Xarray dataset """

        return self.RESULT
    
    # =================================================================================================

    # ========================================================= #
    # Auxiliary Functions for Writing Variables to NetCDF Files
    # ========================================================= #

    def add_variable_along_northingeasting(self, ds, var, name, units, long_name):
        """ This function adds variables to the RESULT Xarray dataset (x,y) """
        ds[name] = (('y','x'), var.data)        
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
    def add_variable_along_northingeastingtime(self, ds, var, name, units, long_name):
        """ This function adds variables to the RESULT Xarray dataset (x,y,t)"""
        ds[name] = (('time','y','x'), var.data)
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
    def add_variable_along_northingeastinglayertime(self, ds, var, name, units, long_name):
        """ This function adds variables to the RESULT Xarray dataset (x,y,z,t) """
        ds[name] = (('time','y','x','layer'), var.data)
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
    # =================================================================================================
    
