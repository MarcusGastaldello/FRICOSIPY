"""
 This file reads the input data (model forcing) and write the output to netcdf file
"""

import os
import sys
import xarray as xr
import pandas as pd
import numpy as np
from numpy import genfromtxt
import csv
import time
from datetime import timedelta
from constants import *
from parameters import *
from config import * 

class IOClass:

    def __init__(self, STATIC = None, METEO = None, ILLUMINATION = None):
        """ Init IO Class"""

        # Read variable list from file
        self.surface_energy_fluxes = surface_energy_fluxes
        self.surface_mass_fluxes = surface_mass_fluxes
        self.subsurface_mass_fluxes = subsurface_mass_fluxes
        self.other = other
        self.subsurface_variables = subsurface_variables

        # Initialise input datasets:
        self.METEO = METEO
        self.STATIC = STATIC
        self.ILLUMINATION = ILLUMINATION
        
    # ===============================
    # Loads the Input STATIC Dataset:
    # ===============================
    def load_static_file(self):
        """ Returns the STATIC xarray dataset"""

        # Open input static dataset 
        self.STATIC = xr.open_dataset(os.path.join(data_path,'static',static_netcdf))

        # Select spatial extent from config.py
        if subset == True:
            self.STATIC = self.STATIC.sel(y = slice(y_min,y_max), x = slice(x_min,x_max))
        
        self.ny = self.STATIC.dims['y']
        self.nx = self.STATIC.dims['x']

        print('\t Spatial Nodes: %s' %(np.nansum(self.STATIC.MASK >= 1)))

        return self.STATIC

    # ==============================
    # Loads the Input METEO Dataset:
    # ==============================

    def load_meteo_file(self):
        """ Returns the METEO xarray dataset"""

        # Open input meteorological dataset
        self.METEO = xr.open_dataset(os.path.join(data_path,'meteo',meteo_netcdf))
        self.METEO['time'] = np.sort(self.METEO['time'].values)

        start_interval=str(self.METEO.time.values[0])[0:16]
        end_interval = str(self.METEO.time.values[-1])[0:16]
        time_steps = str(self.METEO.dims['time'])

        print('\t INFORMATION:')
        print('\t ==============================================================')
        print('\t Max temporal range from %s until %s. Time steps: %s ' % (start_interval, end_interval, time_steps))
        print('\t Integration from %s to %s' % (time_start, time_end))
        print('\t Input Static Dataset: ',static_netcdf)
        print('\t Input Meteorological Dataset: ',meteo_netcdf)
        print('\t Input Illumination Dataset: ',illumination_netcdf)
        print('\t Output Timestamps: ',output_timestamps)       
        print('\t Output Dataset: ',output_netcdf)        
        
        self.METEO = self.METEO.sel(time=slice(time_start, time_end))   # Select temporal range from config.py

        return self.METEO

    # =====================================
    # Loads the Input ILLUMINATION Dataset:
    # =====================================

    def load_illumination_file(self):
        """ Returns the ILLUMINATION xarray dataset"""

        # Open input illumination dataset
        self.ILLUMINATION = xr.open_dataset(os.path.join(data_path,'illumination',illumination_netcdf))

        # Select spatial extent from config.py
        if subset == True:
            self.ILLUMINATION = self.ILLUMINATION.sel(y = slice(y_min,y_max), x = slice(x_min,x_max))

        return self.ILLUMINATION

    # ==================================
    # Creates the RESULT Xarray Dataset:
    # ==================================

    def create_result_file(self):
        """ Returns the data xarray """
        self.init_result_dataset()
        return self.RESULT

    # ======================================
    # Initialises the RESULT Xarray Dataset:
    # ======================================

    def init_result_dataset(self):

        self.RESULT = xr.Dataset()

        # Spatial coordinates
        self.RESULT.coords['y'] = self.STATIC.coords['y']
        self.RESULT.coords['x'] = self.STATIC.coords['x'] 

        # Temporal range      
        self.RESULT.coords['time'] = genfromtxt(os.path.join(data_path,'meteo/Output_Timestamps',output_timestamps), dtype = 'M', delimiter=',', skip_header = True)
        print('\t Output timestamps:', str(self.RESULT.dims['time']))
        print('\t ==============================================================\n')

        # ===================================== #
        # Assign Attributes to the NETCDF File:
        # ===================================== #

        # Global attributes from config.py
        self.RESULT.attrs['Compression_level'] = compression_level
        self.RESULT.attrs['Full_field'] = str(full_field)

        # Global attributes from constants.py

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
        self.RESULT.attrs['Water_percolation_method'] = water_percolation_method
        self.RESULT.attrs['Sfc_temperature_method'] = sfc_temperature_method        

        # Initial Conditions:
        self.RESULT.attrs['Initial_snowheight'] = initial_snowheight
        self.RESULT.attrs['Initial_snow_layer_heights'] = initial_snow_layer_heights
        self.RESULT.attrs['Initial_glacier_height'] = initial_glacier_height
        self.RESULT.attrs['Initial_glacier_layer_heights'] = initial_glacier_layer_heights
        self.RESULT.attrs['Initial_top_density_snowpack'] = initial_top_density_snowpack
        self.RESULT.attrs['Initial_bottom_density_snowpack'] = initial_bottom_density_snowpack
        self.RESULT.attrs['Initial_temperature_bottom'] = initial_temperature_bottom
        self.RESULT.attrs['Initial_temperature_top'] = initial_temperature_top

        # Subsurface Remeshing Options:
        self.RESULT.attrs['Remesh_method'] = remesh_method       
        self.RESULT.attrs['Max_layers'] = max_layers
        self.RESULT.attrs['Minimum_snow_layer_height'] = minimum_snow_layer_height
        self.RESULT.attrs['First_layer_height_log_profile'] = first_layer_height
        self.RESULT.attrs['Layer_stretching_log_profile'] = layer_stretching
        self.RESULT.attrs['Merge_max'] = merge_max
        self.RESULT.attrs['Density_threshold_merging'] = density_threshold_merging
        self.RESULT.attrs['Temperature_threshold_merging'] = temperature_threshold_merging
        self.RESULT.attrs['Maximum_simulation_layer_height'] = maximum_simulation_layer_height
        self.RESULT.attrs['Maximum_coarse_layer_height'] = maximum_coarse_layer_height
        self.RESULT.attrs['Coarse_layer_threshold'] = coarse_layer_threshold
        self.RESULT.attrs['Maximum_glacier_layer_height'] = maximum_glacier_layer_height

        # Model Parameters (General):
        self.RESULT.attrs['Time_step_input_file_seconds'] = dt
        self.RESULT.attrs['Max_simulation_depth'] = max_depth
        self.RESULT.attrs['station_altitude'] = station_altitude
        self.RESULT.attrs['Z_measurment_height'] = z
        self.RESULT.attrs['Albedo_fresh_snow'] = albedo_fresh_snow
        self.RESULT.attrs['Albedo_firn'] = albedo_firn
        self.RESULT.attrs['Albedo_ice'] = albedo_ice
        self.RESULT.attrs['Albedo_mod_snow_depth'] = albedo_mod_snow_depth
        self.RESULT.attrs['alpha'] = alpha
        self.RESULT.attrs['beta'] = beta
        self.RESULT.attrs['Clouds_emissivity_constant'] = e_clouds
        self.RESULT.attrs['Longwave_emission_constant'] = LW_emission_constant
        self.RESULT.attrs['zlt1'] = zlt1
        self.RESULT.attrs['zlt2'] = zlt2
        self.RESULT.attrs['Minimum_snowfall'] = minimum_snowfall
        self.RESULT.attrs['Snow_ice_threshold'] = snow_ice_threshold
        self.RESULT.attrs['Surface_emission_coeff'] = surface_emission_coeff

        # Model Parameters (Parameterisation-specific):
        self.RESULT.attrs['Preferential_percolation_depth'] = z_lim
        self.RESULT.attrs['extinction_coeff_snow'] = extinction_coeff_snow
        self.RESULT.attrs['Albedo_wet_snow_surface'] = t_star_wet
        self.RESULT.attrs['Albedo_dry_snow_surface'] = t_star_dry
        self.RESULT.attrs['Albedo_linear_factor'] = t_star_K
        self.RESULT.attrs['Albedo_cutoff_threshold'] = t_star_cutoff
        self.RESULT.attrs['Albedo_mod_snow_aging'] = albedo_mod_snow_aging
        self.RESULT.attrs['Roughness_fresh_snow'] = roughness_fresh_snow
        self.RESULT.attrs['Roughness_ice'] = roughness_ice
        self.RESULT.attrs['Roughness_firn'] = roughness_firn
        self.RESULT.attrs['Aging_factor_roughness'] = aging_factor_roughness
        self.RESULT.attrs['Density_fresh_snow'] = constant_density
        self.RESULT.attrs['Surface_roughness_constant'] = roughness_constant
        self.RESULT.attrs['z1'] = z1
        self.RESULT.attrs['z2'] = z2

        # Physical Constants:
        self.RESULT.attrs['lat_heat_melting'] = lat_heat_melting
        self.RESULT.attrs['lat_heat_vaporize'] = lat_heat_vaporize
        self.RESULT.attrs['lat_heat_sublimation'] = lat_heat_sublimation
        self.RESULT.attrs['spec_heat_air'] = spec_heat_air
        self.RESULT.attrs['spec_heat_water'] = spec_heat_water
        self.RESULT.attrs['spec_heat_ice'] = spec_heat_ice
        self.RESULT.attrs['k_a'] = k_a
        self.RESULT.attrs['k_w'] = k_w
        self.RESULT.attrs['k_i'] = k_i
        self.RESULT.attrs['air_density'] = air_density
        self.RESULT.attrs['water_density'] = water_density
        self.RESULT.attrs['ice_density'] = ice_density
        self.RESULT.attrs['g'] = g
        self.RESULT.attrs['M'] = M
        self.RESULT.attrs['R'] = R
        self.RESULT.attrs['Atm_Pressure'] = Atm_Pressure
        self.RESULT.attrs['R_watervapour'] = R_watervapour
        self.RESULT.attrs['R_dryair'] = R_dryair
        self.RESULT.attrs['optical_depth'] = optical_depth
        self.RESULT.attrs['exp_aerosol'] = exp_aerosol
        self.RESULT.attrs['sigma'] = sigma
        self.RESULT.attrs['zero_temperature'] = zero_temperature

        # ====================================== #
        # Add Static Variables to Result Dataset
        # ====================================== #

        # Variables given by the input dataset
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ELEVATION, 'ELEVATION', 'm', 'Elevation')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.MASK, 'MASK', 'boolean', 'Glacier mask')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.SLOPE, 'SLOPE', 'degrees', 'Terrain slope')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ASPECT, 'ASPECT', 'degrees', 'Aspect of slope')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.BASAL, 'BASAL', 'mW m-2', 'Basal Heat Flux')
        self.add_variable_along_northingeasting(self.RESULT, self.STATIC.ACCUMULATION, 'ACCUMULATION', 'm a-1', 'Annual Accumulation Climatology')

        return self.RESULT
  
    # ==================== #
    # Global Result Arrays
    # ==================== #

    def create_global_result_arrays(self):

        # Reduce output reporting frequency
        result_timestamps = genfromtxt(os.path.join(data_path,'meteo/Output_Timestamps',output_timestamps), dtype = 'M', delimiter=',', skip_header = True)
        reduced_time = len(result_timestamps)

        # Surface Energy Fluxes (7):
        if ('SHORTWAVE' in self.surface_energy_fluxes):
            self.SHORTWAVE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('LONGWAVE' in self.surface_energy_fluxes):
            self.LONGWAVE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SENSIBLE' in self.surface_energy_fluxes):
            self.SENSIBLE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('LATENT' in self.surface_energy_fluxes):
            self.LATENT = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('GROUND' in self.surface_energy_fluxes):
            self.GROUND = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('RAIN_FLUX' in self.surface_energy_fluxes):
            self.RAIN_FLUX = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('MELT_ENERGY' in self.surface_energy_fluxes):
            self.MELT_ENERGY = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)

        # Surface Mass Fluxes (8):
        if ('RAIN' in self.surface_mass_fluxes):
            self.RAIN = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SNOWFALL' in self.surface_mass_fluxes):
            self.SNOWFALL = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('EVAPORATION' in self.surface_mass_fluxes):
            self.EVAPORATION = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SUBLIMATION' in self.surface_mass_fluxes):
            self.SUBLIMATION = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('CONDENSATION' in self.surface_mass_fluxes):
            self.CONDENSATION = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('DEPOSITION' in self.surface_mass_fluxes):
            self.DEPOSITION = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURFACE_MELT' in self.surface_mass_fluxes):
            self.SURFACE_MELT = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SMB' in self.surface_mass_fluxes):
            self.SMB = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.REFREEZE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.SUBSURFACE_MELT = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.RUNOFF = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('MB' in self.subsurface_mass_fluxes):
            self.MB = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)

        # Other Information (7):
        if ('SNOW_HEIGHT' in self.other):
            self.SNOW_HEIGHT = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('TOTAL_HEIGHT' in self.other):
            self.TOTAL_HEIGHT = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('SURF_TEMP' in self.other):
            self.SURF_TEMP = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('ALBEDO' in self.other):
            self.ALBEDO = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('N_LAYERS' in self.other):
            self.N_LAYERS = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('FIRN_TEMPERATURE' in self.other):
            self.FIRN_TEMPERATURE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.FIRN_TEMPERATURE_CHANGE = np.full((reduced_time,self.ny,self.nx), np.nan, dtype = precision)

        # Subsurface Variables (11):
        if full_field:
            if ('DEPTH' in self.subsurface_variables):
                self.LAYER_DEPTH = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('HEIGHT' in self.subsurface_variables):
                self.LAYER_HEIGHT = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('DENSITY' in self.subsurface_variables):
                self.LAYER_DENSITY = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('TEMPERATURE' in self.subsurface_variables):
                self.LAYER_TEMPERATURE = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('WATER_CONTENT' in self.subsurface_variables):
                self.LAYER_WATER_CONTENT = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('COLD_CONTENT' in self.subsurface_variables):
                self.LAYER_COLD_CONTENT = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('POROSITY' in self.subsurface_variables):
                self.LAYER_POROSITY = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('ICE_FRACTION' in self.subsurface_variables):
                self.LAYER_ICE_FRACTION = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('IRREDUCIBLE_WATER' in self.subsurface_variables):
                self.LAYER_IRREDUCIBLE_WATER = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('REFREEZE' in self.subsurface_variables):
                self.LAYER_REFREEZE = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
            if ('YEAR' in self.subsurface_variables):
                self.LAYER_YEAR = np.full((reduced_time,self.ny,self.nx,max_layers), np.nan, dtype = precision)
    
    # ================================================= #
    # Assign Local Node Results to Global Result Arrays
    # ================================================= #
    
    def copy_local_to_global(self,y,x,
        local_SHORTWAVE,local_LONGWAVE,local_SENSIBLE,local_LATENT,local_GROUND,local_RAIN_FLUX,local_MELT_ENERGY, \
        local_RAIN,local_SNOWFALL,local_EVAPORATION,local_SUBLIMATION,local_CONDENSATION,local_DEPOSITION,local_SURFACE_MELT,local_SMB, \
        local_REFREEZE,local_SUBSURFACE_MELT,local_RUNOFF,local_MB, \
        local_SNOW_HEIGHT,local_TOTAL_HEIGHT,local_SURF_TEMP,local_ALBEDO,local_N_LAYERS,local_FIRN_TEMPERATURE,local_FIRN_TEMPERATURE_CHANGE, \
        local_LAYER_DEPTH,local_LAYER_HEIGHT,local_LAYER_DENSITY,local_LAYER_TEMPERATURE,local_LAYER_WATER_CONTENT,local_LAYER_COLD_CONTENT,local_LAYER_POROSITY,local_LAYER_ICE_FRACTION, \
        local_LAYER_IRREDUCIBLE_WATER,local_LAYER_REFREEZE,local_LAYER_YEAR):
        
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
        if ('SMB' in self.surface_mass_fluxes):
            self.SMB[:,y,x] = local_SMB

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.REFREEZE[:,y,x] = local_REFREEZE
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.SUBSURFACE_MELT[:,y,x] = local_SUBSURFACE_MELT
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.RUNOFF[:,y,x] = local_RUNOFF
        if ('MB' in self.subsurface_mass_fluxes):
            self.MB[:,y,x] = local_MB         

        # Other Information (7):
        if ('SNOW_HEIGHT' in self.other):
            self.SNOW_HEIGHT[:,y,x] = local_SNOW_HEIGHT
        if ('TOTAL_HEIGHT' in self.other):
            self.TOTAL_HEIGHT[:,y,x] = local_TOTAL_HEIGHT
        if ('SURF_TEMP' in self.other):
            self.SURF_TEMP[:,y,x] = local_SURF_TEMP
        if ('ALBEDO' in self.other):
            self.ALBEDO[:,y,x] = local_ALBEDO
        if ('N_LAYERS' in self.other):
            self.N_LAYERS[:,y,x] = local_N_LAYERS
        if ('FIRN_TEMPERATURE' in self.other):
            self.FIRN_TEMPERATURE[:,y,x] = local_FIRN_TEMPERATURE
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.FIRN_TEMPERATURE_CHANGE[:,y,x] = local_FIRN_TEMPERATURE_CHANGE
        
        # Subsurface Variables (11):
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
            if ('YEAR' in self.subsurface_variables):
                self.LAYER_YEAR[:,y,x,:] = local_LAYER_YEAR

    # =================================== #
    # Write Results to Output NETCDF File
    # =================================== #

    def write_results_to_file(self):

        # Surface Energy Fluxes (7):
        if ('SHORTWAVE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SHORTWAVE, 'SHORTWAVE', 'W m^-2', 'Shortwave Flux')
        if ('LONGWAVE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.LONGWAVE, 'LONGWAVE', 'W m^-2', 'Longwave Flux')
        if ('SENSIBLE' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SENSIBLE, 'SENSIBLE', 'W m^-2', 'Sensible Flux')
        if ('LATENT' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.LATENT, 'LATENT', 'W m^-2', 'Latent Flux')
        if ('GROUND' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.GROUND, 'GROUND', 'W m^-2', 'Ground Flux')
        if ('RAIN_FLUX' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RAIN_FLUX, 'RAIN_FLUX', 'W m^-2', 'Rain Heat Flux')
        if ('MELT_ENERGY' in self.surface_energy_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.MELT_ENERGY, 'MELT_ENERGY', 'W m^-2', 'Melt Flux')

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
        if ('SMB' in self.surface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SMB, 'SMB', 'm w.e.', 'Surface Mass Balance')

        # Subsurface Mass Fluxes (4):
        if ('REFREEZE' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.REFREEZE, 'REFREEZE', 'm w.e.', 'Refreezing')
        if ('SUBSURFACE_MELT' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SUBSURFACE_MELT, 'SUBSURFACE_MELT', 'm w.e.', 'Subsurface Melt')
        if ('RUNOFF' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.RUNOFF, 'RUNOFF', 'm w.e.', 'Surface Runoff')
        if ('MB' in self.subsurface_mass_fluxes):
            self.add_variable_along_northingeastingtime(self.RESULT, self.MB, 'MB', 'm w.e.', 'Mass Balance')       

        # Other Information (7):
        if ('SNOW_HEIGHT' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SNOW_HEIGHT, 'SNOW_HEIGHT', 'm', 'Snow Height')
        if ('TOTAL_HEIGHT' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.TOTAL_HEIGHT, 'TOTAL_HEIGHT', 'm', 'Total Height')
        if ('SURF_TEMP' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.SURF_TEMP, 'SURF_TEMP', 'C', 'Surface Temperature')
        if ('ALBEDO' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.ALBEDO, 'ALBEDO', '-', 'Albedo')
        if ('NLAYERS' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.NLAYERS, 'N_LAYERS', 'n', 'Number of Layers')
        if ('FIRN_TEMPERATURE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FIRN_TEMPERATURE, 'FIRN_TEMPERATURE', 'C', 'Firn Temperature at x m Depth')
        if ('FIRN_TEMPERATURE_CHANGE' in self.other):
            self.add_variable_along_northingeastingtime(self.RESULT, self.FIRN_TEMPERATURE_CHANGE, 'FIRN_TEMP_CHANGE', 'ΔC', 'Firn Warming at x m Depth')

        # Subsurface Variables (11):
        if full_field:
            if ('DEPTH' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_DEPTH, 'LAYER_DEPTH', 'm', 'Layer Depth')
            if ('HEIGHT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_HEIGHT, 'LAYER_HEIGHT', 'm', 'Layer Height') 
            if ('DENSITY' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_DENSITY, 'LAYER_DENSITY', 'kg m^-3', 'Layer Density') 
            if ('TEMPERATURE' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_TEMPERATURE, 'LAYER_TEMPERATURE', 'K', 'Layer Temperature') 
            if ('WATER_CONTENT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_WATER_CONTENT, 'LAYER_WATER_CONTENT', 'kg m^-2', 'Liquid Water Content') 
            if ('COLD_CONTENT' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_COLD_CONTENT, 'LAYER_COLD_CONTENT', 'J m^-2', 'Cold Content') 
            if ('POROSITY' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_POROSITY, 'LAYER_POROSITY', '-', 'Porosity') 
            if ('ICE_FRACTION' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_ICE_FRACTION, 'LAYER_ICE_FRACTION', '-', 'Ice Fraction') 
            if ('IRREDUCIBLE_WATER' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_IRREDUCIBLE_WATER, 'LAYER_IRR_WATER', '-', 'Irreducible Water') 
            if ('REFREEZE' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_REFREEZE, 'LAYER_REFREEZE', 'm w.e.', 'Refreezing')   
            if ('YEAR' in self.subsurface_variables):
                self.add_variable_along_northingeastinglayertime(self.RESULT, self.LAYER_YEAR, 'LAYER_YEAR', 'yyyy', 'Year')       

    def get_result(self):
        return self.RESULT

    # ========================================================= #
    # Auxiliary Functions for Writing Variables to NetCDF Files
    # ========================================================= #

    def add_variable_along_northingeasting(self, ds, var, name, units, long_name):
        """ This function self.adds missing variables to the self.RESULT class """
        ds[name] = (('y','x'), var.data)        
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
    def add_variable_along_northingeastingtime(self, ds, var, name, units, long_name):
        """ This function self.adds missing variables to the self.RESULT class """
        ds[name] = (('time','y','x'), var.data)
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
    def add_variable_along_northingeastinglayertime(self, ds, var, name, units, long_name):
        """ This function self.adds missing variables to the self.RESULT class """
        ds[name] = (('time','y','x','layer'), var.data)
        ds[name].attrs['units'] = units
        ds[name].attrs['long_name'] = long_name
        ds[name].encoding['_FillValue'] = -9999
        return ds
    
