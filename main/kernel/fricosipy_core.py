import numpy as np
import pandas as pd
from numpy import genfromtxt
from datetime import datetime
import datetime as dt
import os
import sys

from constants import *
from parameters import *
from config import *
from main.modules.albedo import update_albedo
from main.modules.thermal_diffusion import thermal_diffusion
from main.modules.penetrating_radiation import penetrating_radiation
from main.modules.percolation_refreezing import percolation_refreezing
from main.modules.densification import densification
from main.modules.shortwave_radiation import TOA_insolation, shortwave_radiation_input
from main.modules.surface_temperature import update_surface_temperature
from main.modules.surface_roughness import update_roughness
from main.kernel.init import init_snowpack
from main.kernel.io import IOClass


def fricosipy_core(STATIC, METEO, ILLUMINATION, indY, indX):
    """ Cosipy core function, which perform the calculations on one core.

    Variables:
    ======
    STATIC: Xarray dataset containing topographic/static data (x,y)
    METEO: Xarray dataset containing meteoroligical data (t)
    ILLUMINATION: Xarray dataset containing solar illumination data (x,y,t)

    Returns
    ======
    Returns all calculated variables of one grid point

    """

    # =================== #
    # INITIALISE SNOWPACK
    # =================== #
    GRID = init_snowpack()

    # ========================= #
    # GET STATIC DATA FROM FILE
    # ========================= #

    ELEVATION = STATIC.ELEVATION.values
    SLOPE = STATIC.SLOPE.values
    ASPECT = STATIC.ASPECT.values
    LATITUDE = STATIC.LATITUDE.values
    LONGITUDE = STATIC.LONGITUDE.values

    if 'BASAL' in list(STATIC.keys()):
        BASAL = STATIC.BASAL.values
    else:
        BASAL = basal_heat_flux

    if 'ACCUMULATION' in list(STATIC.keys()):
        ACCUMULATION = STATIC.ACCUMULATION.values
    else:
        ACCUMULATION = None

    # ================================= #
    # GET METEOROLOGICAL DATA FROM FILE
    # ================================= #

    # Interpolate temperature using an air temperature lapse rate
    if 'T2_LAPSE' in list(METEO.keys()):
        T2 = METEO.T2.values + (ELEVATION - station_altitude) * METEO.T2_LAPSE.values
    else:
        T2 = METEO.T2.values + (ELEVATION - station_altitude) * air_temperature_lapse_rate

    # Interpolate atmospheric pressure using the barometric equation
    np.seterr(divide = 'ignore') 
    if 'T2_LAPSE' in list(METEO.keys()):
        PRES = np.where(METEO.T2_LAPSE.values == 0,  
                        METEO.PRES.values * np.exp(((-g * M) * (ELEVATION - station_altitude))/(R * METEO.T2.values)),
                        METEO.PRES.values * np.power((T2/METEO.T2.values),((-g * M) / (R * METEO.T2_LAPSE.values))))
    else:
        PRES = METEO.PRES.values * np.power((T2/METEO.T2.values),((-g * M) / (R * -0.006)))
    
    # Standard precipiation data [mm] (Van Pelt et al., 2019) 
    if 'RRR' in list(METEO.keys()):
        RRR = METEO.RRR.values * (1 + (ELEVATION - station_altitude) * precipitation_lapse_rate) * precipitation_multiplier

    # Three phase accumulation model (Accumulation climatology [m] * Annual anomaly [-] * Downscaling coefficient) [mm]
    elif ('ACCUMULATION' in list(STATIC.keys())) and ('ACC_ANOMALY' in list(METEO.keys())) and ('D' in list(METEO.keys())):

        # Correction for sublimation losses (if known):
        if ('SUBLIMATION' in list(STATIC.keys())) and ('SUB_ANOMALY' in list(METEO.keys())):
            RRR = ((STATIC.ACCUMULATION.values * METEO.ACC_ANOMALY.values) + (STATIC.SUBLIMATION.values * METEO.SUB_ANOMALY.values)) * METEO.D.values * 1000 * precipitation_multiplier
        else:
            RRR = STATIC.ACCUMULATION.values * METEO.ACC_ANOMALY.values * METEO.D.values * 1000 * precipitation_multiplier

    else:
        print("Either Precipitation ('RRR') or the variables of the three phase accumulation model ('ACC_ANOMALY','D','ACCUMULATION') must be supplied in the input METEO & STATIC files")
        sys.exit()

    # Remaining variables remain constant across the spatial grid
    RH2 = METEO.RH2.values
    U2 = METEO.U2.values
    MONTH = METEO.time.dt.month.values
    YEAR = METEO.time.dt.year.values
    HYDRO_YEAR = np.where(MONTH < 10, YEAR, YEAR + 1)

    # Albedo (measured):
    if 'ALBEDO' in list(METEO.keys()):
        ALBEDO = METEO.ALBEDO.values

    # Radiative fluxes (SWin & LWin):
    if ('SWin' in list(METEO.keys())) and ('LWin' in list(METEO.keys())):
        SWin = METEO.SWin.values
        LWin = METEO.LWin.values
        N = None

    # Input shortwave radiation (SWin) and fractional cloud cover (N):
    elif ('SWin' in list(METEO.keys())) and ('N' in list(METEO.keys())):
        SWin = METEO.SWin.values
        N = METEO.N.values
        LWin = None

    # Fractional cloud cover (N) only:
    elif 'N' in list(METEO.keys()):
        N = METEO.N.values
        SWin = None
        LWin = None

    # Radiative fluxes error message:
    else:
        print("Either Fractional cloud cover ('N') or incoming Longwave radiation ('LWin') must be supplied in the input METEO file")
        sys.exit()

    # =============================== #
    # GET ILLUMINATION DATA FROM FILE
    # =============================== #

    ILLUMINATION_NORM = ILLUMINATION.ILLUMINATION_NORM.values # Illumination (Normal Year)
    ILLUMINATION_LEAP = ILLUMINATION.ILLUMINATION_LEAP.values # Illumination (Leap Year)

    # =================== #
    # SHORTWAVE RADIATION
    # =================== #

    # Top of Atmosphere (TOA) Radiation
    DOY = METEO.time.dt.dayofyear.values       # Day of Year
    HOUR = METEO.time.dt.hour.values           # Hour
    LEAP = METEO.time.dt.is_leap_year.values   # Leap Year (Boolean)
    HOY = ((DOY - 1) * 24) + HOUR              # Hour of Year    
    TOA_INSOL, TOA_INSOL_FLAT, TOA_INSOL_NORM = TOA_insolation(LATITUDE, LONGITUDE, SLOPE, ASPECT, HOUR, LEAP, HOY)

    # Illumination
    NODE_ILLUMINATION = np.where(LEAP,ILLUMINATION_LEAP[HOY],ILLUMINATION_NORM[HOY]) 

    # Input Shortwave Radiation
    if ('SWin' in list(METEO.keys())):
        SWin, N = shortwave_radiation_input(PRES, T2, RH2, TOA_INSOL, TOA_INSOL_FLAT, TOA_INSOL_NORM, NODE_ILLUMINATION, SWin = SWin)
    elif ('N' in list(METEO.keys())):
        SWin, _ = shortwave_radiation_input(PRES, T2, RH2, TOA_INSOL, TOA_INSOL_FLAT, TOA_INSOL_NORM, NODE_ILLUMINATION, N = N)
    
    # ==================== #
    # LOCAL RESULT VARIABLES
    # ==================== #
    
    # Extract result timesteps from file:
    result_timesteps = genfromtxt(os.path.join(data_path,'meteo/Output_Timestamps',output_timestamps), dtype = 'M', delimiter=',', skip_header = True)
    
    # Convert from datetime [ns] to simulation index:
    result_timesteps = ((result_timesteps - METEO.time[0].data).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)
    nt = len(result_timesteps)

    # Spin-up end index:
    # Convert from datetime [ns] to simulation index:
    spin_up_end_timestep = ((pd.to_datetime(spin_up_end).to_numpy() - pd.to_datetime(time_start).to_numpy()).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)
    time_end_timestep = ((pd.to_datetime(time_end).to_numpy() - pd.to_datetime(time_start).to_numpy()).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)
    if time_end_timestep in result_timesteps:
        if model_spin_up == True:
            aggregation_timestep_range = np.diff(np.insert(result_timesteps,0,spin_up_end_timestep))
        else:
            aggregation_timestep_range = np.diff(np.insert(result_timesteps,0,0))
    else:
        if model_spin_up == True:
            aggregation_timestep_range = np.diff(np.insert(np.append(result_timesteps,time_end_timestep),0,spin_up_end_timestep))
        else:
            aggregation_timestep_range = np.diff(np.insert(np.append(result_timesteps,time_end_timestep),0,0))


    # Meteorological Variables (5):
    _AIR_TEMPERATURE = np.full(nt,np.nan, dtype=precision)
    _AIR_PRESSURE = np.full(nt,np.nan, dtype=precision)
    _RELATIVE_HUMIDITY = np.full(nt,np.nan, dtype=precision)
    _WIND_SPEED = np.full(nt,np.nan, dtype=precision)
    _FRACTIONAL_CLOUD_COVER = np.full(nt,np.nan, dtype=precision)

    # Surface Energy Fluxes (7):
    _SWnet = np.full(nt,np.nan, dtype=precision)
    _LWnet = np.full(nt,np.nan, dtype=precision)
    _SENSIBLEnet = np.full(nt,np.nan, dtype=precision)
    _LATENTnet = np.full(nt,np.nan, dtype=precision)
    _GROUNDnet = np.full(nt,np.nan, dtype=precision)
    _RAIN_FLUX = np.full(nt,np.nan, dtype=precision)
    _MELT_ENERGY = np.full(nt,np.nan, dtype=precision)

    # Surface Mass Fluxes (8):
    _RAIN = np.full(nt,np.nan, dtype=precision)
    _SNOWFALL = np.full(nt,np.nan, dtype=precision)
    _EVAPORATION = np.full(nt,np.nan, dtype=precision)
    _SUBLIMATION = np.full(nt,np.nan, dtype=precision)
    _CONDENSATION = np.full(nt,np.nan, dtype=precision)
    _DEPOSITION = np.full(nt,np.nan, dtype=precision)
    _SURFACE_MELT = np.full(nt,np.nan, dtype=precision)
    _SMB = np.full(nt,np.nan, dtype=precision)

    # Subsurface Mass Fluxes (4):
    _REFREEZE = np.full(nt,np.nan, dtype=precision)
    _SUBSURFACE_MELT = np.full(nt,np.nan, dtype=precision)
    _RUNOFF = np.full(nt,np.nan, dtype=precision)
    _MB = np.full(nt,np.nan, dtype=precision)

    # Other Information (8):
    _SNOW_HEIGHT = np.full(nt,np.nan, dtype=precision)
    _TOTAL_HEIGHT = np.full(nt,np.nan, dtype=precision)
    _SURFACE_TEMPERATURE = np.full(nt,np.nan, dtype=precision)
    _SURFACE_ALBEDO = np.full(nt,np.nan, dtype=precision)
    _N_LAYERS = np.full(nt,np.nan, dtype=precision)     
    _FIRN_TEMPERATURE = np.full(nt,np.nan, dtype=precision)
    _FIRN_TEMPERATURE_CHANGE = np.full(nt,np.nan, dtype=precision)
    _FIRN_FACIE = np.zeros(nt, dtype ='int32')

    # Subsurface Variables (11):
    _LAYER_DEPTH = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_HEIGHT = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_DENSITY = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_TEMPERATURE = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_WATER_CONTENT = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_COLD_CONTENT = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_POROSITY = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_ICE_FRACTION = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_IRREDUCIBLE_WATER = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_REFREEZE = np.full((nt,max_layers), np.nan, dtype=precision)
    _LAYER_HYDRO_YEAR = np.full((nt,max_layers), np.nan, dtype=precision)

    # ========= #
    # TIME LOOP
    # ========= #

    # Initial Variables:
    cumulative_melt = 0.0
    surface_temperature = 270
    Initial_Firn_Temperature = np.nan
    albedo_snow = albedo_fresh_snow

    n = 0
    idx = 0
    for t in np.arange(len(METEO.time.values)):

        # ============= #
        # PRECIPITATION
        # ============= #

        # Check grid
        GRID.grid_check()

        # Calc fresh snow density
        if snow_density_method =='Vionnet12':
            density_fresh_snow = np.maximum(109.0+6.0*(T2[t]-273.16)+26.0*np.sqrt(U2[t]), 50.0)
        elif snow_density_method =='constant':
            density_fresh_snow = constant_density 

        # Derive snowfall [m] and rain rates [m w.e.]
        # Convert total precipitation [mm] to snowheight [m]; liquid/solid fraction
        SNOWFALL = (RRR[t]/1000.0)*(water_density/density_fresh_snow)*(0.5*(-np.tanh((T2[t]-zero_temperature)) + 1.0))
        RAIN = RRR[t] - SNOWFALL*(density_fresh_snow/water_density) * 1000.0

        # if snowfall is smaller than the threshold
        if SNOWFALL<minimum_snowfall:
            SNOWFALL = 0.0

        # if rainfall is smaller than the threshold
        if RAIN<(minimum_snowfall*(density_fresh_snow/water_density)*1000.0):
            RAIN = 0.0

        if SNOWFALL > 0.0:
            # Add a new snow node on top
           GRID.add_fresh_snow(SNOWFALL, density_fresh_snow, np.minimum(float(T2[t]),zero_temperature), 0.0)
           GRID.set_node_hydro_year(0, float(HYDRO_YEAR[t])) # Set the uppermost subsurface layer as the current hydrological year of accumulation
        else:
           GRID.set_fresh_snow_props_update_time(dt)

        # =========== #
        # REMESH GRID
        # =========== #

        # Update subsurface grid (if necessary)
        GRID.update_grid()

        # ======================================= #
        # ALBEDO & SHORTWAVE RADIATION COMPONENTS
        # ======================================= #       

        # Update Albedo
        if albedo_method == 'measured':
            albedo = ALBEDO[t]
        else:
            albedo, albedo_snow = update_albedo(GRID, albedo_snow, surface_temperature)

        # Calculate net shortwave radiation
        SWnet = SWin[t] * (1 - albedo)

        # Penetrating SW radiation and subsurface melt
        if SWnet > 0.0:
            subsurface_melt, G_penetrating = penetrating_radiation(GRID, SWnet, dt)
        else:
            subsurface_melt = 0.0
            G_penetrating = 0.0

        # Calculate residual net shortwave radiation (penetrating part removed)
        sw_radiation_net = SWnet - G_penetrating

        # ================= #
        # SURFACE ROUGHNESS
        # ================= #

        z0 = update_roughness(GRID)

        # ====================== #
        # SURFACE ENERGY BALANCE
        # ====================== #
        
        if LWin is not None:
            # Find new surface temperature (LW is directly supplied from meteorological data)
            fun, surface_temperature, lw_radiation_in, lw_radiation_out, sensible_heat_flux, latent_heat_flux, \
            ground_heat_flux, rain_heat_flux, rho, Lv, MOL, Cs_t, Cs_q, q0, q2 \
            = update_surface_temperature(GRID, dt, z, z0, T2[t], RH2[t], PRES[t], sw_radiation_net, U2[t], RAIN, SLOPE, LWin = LWin[t])

        else:
            # Find new surface temperature (LW is parametrized using cloud fraction)
            fun, surface_temperature, lw_radiation_in, lw_radiation_out, sensible_heat_flux, latent_heat_flux, \
            ground_heat_flux, rain_heat_flux, rho, Lv, MOL, Cs_t, Cs_q, q0, q2 \
            = update_surface_temperature(GRID, dt, z, z0, T2[t], RH2[t], PRES[t], sw_radiation_net, U2[t], RAIN, SLOPE, N = N[t])

        # ============================ #
        # SURFACE MASS FLUXES [m w.e.]
        # ============================ #

        if surface_temperature < zero_temperature:
            sublimation = min(latent_heat_flux / (water_density * lat_heat_sublimation), 0) * dt
            deposition = max(latent_heat_flux / (water_density * lat_heat_sublimation), 0) * dt
            evaporation = 0
            condensation = 0
        else:
            sublimation = 0
            deposition = 0
            evaporation = min(latent_heat_flux / (water_density * lat_heat_vaporize), 0) * dt
            condensation = max(latent_heat_flux / (water_density * lat_heat_vaporize), 0) * dt

        # Ensure melt has occured and this is not just a residual from the SEB solver. 
        if surface_temperature ==  zero_temperature:

            # Melt energy in [W m^-2]
            melt_energy = max(0, sw_radiation_net + lw_radiation_in + lw_radiation_out + ground_heat_flux + rain_heat_flux +
                          sensible_heat_flux + latent_heat_flux)
        else:
            melt_energy = 0.0

        # Convert melt energy to melt mass [m w.e.]
        surface_melt = melt_energy * dt / (water_density * lat_heat_melting)
        cumulative_melt = cumulative_melt + surface_melt + subsurface_melt

        # Net mass change:
        net_mass_change = - surface_melt - sublimation + deposition
        
        # Add mass [m w.e.]
        if net_mass_change > 0:
            pass
            #GRID.add_mass(net_mass_change)

        # Remove mass [m w.e.]
        if net_mass_change < 0:
            GRID.remove_mass(-net_mass_change)

        # Exit node simulation if all snow/glacier layers are removed
        if GRID.get_number_layers() == 0:
            break

        # ======================== #
        # PERCOLATION & REFREEZING
        # ======================== #
        
        # Calculate surface water [m w.e.]
        surface_water = max(surface_melt + condensation - evaporation + RAIN/1000.0, 0) 
        
        # Calculate run-off and refreezing
        if (np.any(GRID.get_liquid_water_content()) or surface_water != 0):
            Q , water_refrozen = percolation_refreezing(GRID,HYDRO_YEAR[t],surface_water)
        else:
            Q , water_refrozen = 0, 0

        # ================= #
        # THERMAL DIFFUSION
        # ================= #
    
        if GRID.get_number_layers() > 1:
            thermal_diffusion(GRID, BASAL, dt)
    
        # ================= #
        # DRY DENSIFICATION
        # ================= #

        densification(GRID, ACCUMULATION, dt)

        # ============ #
        # MASS BALANCE
        # ============ #

        surface_mass_balance = SNOWFALL * (density_fresh_snow / water_density) - surface_melt + sublimation + deposition + evaporation
        internal_mass_balance = water_refrozen - subsurface_melt
        mass_balance = surface_mass_balance + internal_mass_balance

        # ================== #
        # INITIAL CONDITIONS
        # ================== #

        # Setup Aggregated Variable Arrays:
        if ((model_spin_up == True) and (t == spin_up_end_timestep)) or ((model_spin_up == False) and (t == 0)):

            # Aggregated Meteorological Data (5):
            AIR_TEMPERATURE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            AIR_PRESSURE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            RELATIVE_HUMIDITY_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            WIND_SPEED_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            FRACTIONAL_CLOUD_COVER_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

            # Aggregated Energy Fluxes (7):
            SHORTWAVE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            LONGWAVE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SENSIBLE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            LATENT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            GROUND_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            RAIN_FLUX_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            MELT_ENERGY_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

            # Aggregated Surface Mass Fluxes (8):
            RAIN_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SNOWFALL_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            EVAPORATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SUBLIMATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            CONDENSATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            DEPOSITION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SURFACE_MELT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SMB_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

            # Aggregated Subsurface Mass Fluxes (4):
            REFREEZING_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            SUSBSURFACE_MELT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            RUNOFF_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
            MB_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

            # Reset result step index
            n = -1

            # Calculate initial firn temperature
            Index_Depth = np.searchsorted(GRID.get_depth(), firn_temperature_depth, side="left")   
            Initial_Firn_Temperature = GRID.get_temperature()[Index_Depth] - 273.16

        # ================ #
        # DATA AGGREGATION
        # ================ #

        # Store Aggregated Variables:
        if ((model_spin_up == True) and (t > spin_up_end_timestep)) or (model_spin_up == False):

            # Aggregated Meteorological Data (5):
            AIR_TEMPERATURE_AGG[n] = T2[t]
            AIR_PRESSURE_AGG[n] = PRES[t]
            RELATIVE_HUMIDITY_AGG[n] = RH2[t]
            WIND_SPEED_AGG[n] = U2[t]
            FRACTIONAL_CLOUD_COVER_AGG[n] = N[t]

            # Aggregated Energy Fluxes (7):
            SHORTWAVE_AGG[n] = sw_radiation_net
            LONGWAVE_AGG[n] = lw_radiation_in + lw_radiation_out
            SENSIBLE_AGG[n] = sensible_heat_flux
            LATENT_AGG[n] = latent_heat_flux
            GROUND_AGG[n] = ground_heat_flux
            RAIN_FLUX_AGG[n] = rain_heat_flux
            MELT_ENERGY_AGG[n] = melt_energy

            # Aggregated Surface Mass Fluxes (8):
            RAIN_AGG[n] = RAIN / 1000
            SNOWFALL_AGG[n] = SNOWFALL * (density_fresh_snow/water_density)
            EVAPORATION_AGG[n] = evaporation
            SUBLIMATION_AGG[n] = sublimation
            CONDENSATION_AGG[n] = condensation
            DEPOSITION_AGG[n] = deposition
            SURFACE_MELT_AGG[n] = surface_melt
            SMB_AGG[n] = surface_mass_balance

            # Aggregated Subsurface Mass Fluxes (4):
            REFREEZING_AGG[n] = water_refrozen
            SUSBSURFACE_MELT_AGG[n] = subsurface_melt
            RUNOFF_AGG[n] = Q
            MB_AGG[n] = mass_balance   

        # ============== #
        # RESULT WRITING
        # ============== #

        if (t in result_timesteps):

            # Aggregated Meteorological Data (5):
            _AIR_TEMPERATURE[idx] = AIR_TEMPERATURE_AGG.mean()
            _AIR_PRESSURE[idx] = AIR_PRESSURE_AGG.mean()
            _RELATIVE_HUMIDITY[idx] = RELATIVE_HUMIDITY_AGG.mean()
            _WIND_SPEED[idx] = WIND_SPEED_AGG.mean()
            _FRACTIONAL_CLOUD_COVER[idx] = FRACTIONAL_CLOUD_COVER_AGG.mean()

            # Surface Energy Fluxes (Average Aggregated) (7):
            _SWnet[idx] = SHORTWAVE_AGG.mean()
            _LWnet[idx] = LONGWAVE_AGG.mean()
            _SENSIBLEnet[idx] = SENSIBLE_AGG.mean()
            _LATENTnet[idx] = LATENT_AGG.mean()
            _GROUNDnet[idx] = GROUND_AGG.mean()
            _RAIN_FLUX[idx] = RAIN_FLUX_AGG.mean()
            _MELT_ENERGY[idx] = MELT_ENERGY_AGG.mean()

            # Surface Mass Fluxes (Cumulative Aggregated) (8):
            _RAIN[idx] = RAIN_AGG.sum()
            _SNOWFALL[idx] = SNOWFALL_AGG.sum()
            _EVAPORATION[idx] = EVAPORATION_AGG.sum()
            _SUBLIMATION[idx] = SUBLIMATION_AGG.sum()
            _CONDENSATION[idx] = CONDENSATION_AGG.sum()
            _DEPOSITION[idx] = DEPOSITION_AGG.sum()
            _SURFACE_MELT[idx] = SURFACE_MELT_AGG.sum()
            _SMB[idx] = SMB_AGG.sum()

            # Subsurface Mass Fluxes (Cumulative Aggregated) (4):
            _REFREEZE[idx] = REFREEZING_AGG.sum()
            _SUBSURFACE_MELT[idx] = SUSBSURFACE_MELT_AGG.sum()
            _RUNOFF[idx] = RUNOFF_AGG.sum()
            _MB[idx] = MB_AGG.sum()

            # Other Information (Instantaneous) (7):
            _SNOW_HEIGHT[idx] = GRID.get_total_snowheight()
            _TOTAL_HEIGHT[idx] = GRID.get_total_height()
            _SURFACE_TEMPERATURE[idx] = surface_temperature
            _SURFACE_ALBEDO[idx] = albedo
            _N_LAYERS[idx] = GRID.get_number_layers()

            # Calculate Firn temperatures:
            Index_Depth = np.searchsorted(GRID.get_depth(), firn_temperature_depth, side="left")
            _FIRN_TEMPERATURE[idx] = GRID.get_temperature()[Index_Depth] - zero_temperature
            _FIRN_TEMPERATURE_CHANGE[idx] = _FIRN_TEMPERATURE[idx] - Initial_Firn_Temperature

            # Determine Firn Facie:
            if GRID.get_temperature()[Index_Depth] - zero_temperature > 0.1:
                _FIRN_FACIE[idx] = 4
            elif cumulative_melt == 0:
                _FIRN_FACIE[idx] = 1
            elif not np.any(GRID.get_firn_refreeze()):
                _FIRN_FACIE[idx] = 2
            else:
                _FIRN_FACIE[idx] = 3

            # Subsurface Variables (Instantaneous) (11):
            if full_field:
                if GRID.get_number_layers() > max_layers:
                    _LAYER_DEPTH[idx, 0:max_layers] = GRID.get_depth()[0:max_layers]
                    _LAYER_HEIGHT[idx, 0:max_layers] = GRID.get_height()[0:max_layers]
                    _LAYER_DENSITY[idx, 0:max_layers] = GRID.get_density()[0:max_layers]
                    _LAYER_TEMPERATURE[idx, 0:max_layers] = GRID.get_temperature()[0:max_layers]
                    _LAYER_WATER_CONTENT[idx, 0:max_layers] = GRID.get_liquid_water_content()[0:max_layers]
                    _LAYER_COLD_CONTENT[idx, 0:max_layers] = GRID.get_cold_content()[0:max_layers]
                    _LAYER_POROSITY[idx, 0:max_layers] = GRID.get_porosity()[0:max_layers]
                    _LAYER_ICE_FRACTION[idx, 0:max_layers] = GRID.get_ice_fraction()[0:max_layers]
                    _LAYER_IRREDUCIBLE_WATER[idx, 0:max_layers] = GRID.get_irreducible_water_content()[0:max_layers]
                    _LAYER_REFREEZE[idx, 0:max_layers] = GRID.get_refreeze()[0:max_layers]
                    _LAYER_HYDRO_YEAR[idx, 0:max_layers] = GRID.get_hydro_year()[0:max_layers]
                else:
                    _LAYER_DEPTH[idx, 0:GRID.get_number_layers()] = GRID.get_depth()
                    _LAYER_HEIGHT[idx, 0:GRID.get_number_layers()] = GRID.get_height()
                    _LAYER_DENSITY[idx, 0:GRID.get_number_layers()] = GRID.get_density()
                    _LAYER_TEMPERATURE[idx, 0:GRID.get_number_layers()] = GRID.get_temperature()
                    _LAYER_WATER_CONTENT[idx, 0:GRID.get_number_layers()] = GRID.get_liquid_water_content()
                    _LAYER_COLD_CONTENT[idx, 0:GRID.get_number_layers()] = GRID.get_cold_content()
                    _LAYER_POROSITY[idx, 0:GRID.get_number_layers()] = GRID.get_porosity()
                    _LAYER_ICE_FRACTION[idx, 0:GRID.get_number_layers()] = GRID.get_ice_fraction()
                    _LAYER_IRREDUCIBLE_WATER[idx, 0:GRID.get_number_layers()] = GRID.get_irreducible_water_content()
                    _LAYER_REFREEZE[idx, 0:GRID.get_number_layers()] = GRID.get_refreeze()
                    _LAYER_HYDRO_YEAR[idx, 0:GRID.get_number_layers()] = GRID.get_hydro_year()
        
            else:
                _LAYER_DEPTH = None
                _LAYER_HEIGHT = None
                _LAYER_DENSITY = None
                _LAYER_TEMPERATURE = None
                _LAYER_WATER_CONTENT = None
                _LAYER_COLD_CONTENT = None
                _LAYER_POROSITY = None
                _LAYER_ICE_FRACTION = None
                _LAYER_IRREDUCIBLE_WATER = None
                _LAYER_REFREEZE = None
                _LAYER_HYDRO_YEAR = None
            
            # Increase result index:
            idx += 1

            # Reset Aggregation Arrays:
            if idx < nt:

                # Aggregated Meteorological Data (5):
                AIR_TEMPERATURE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                AIR_PRESSURE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                RELATIVE_HUMIDITY_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                WIND_SPEED_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                FRACTIONAL_CLOUD_COVER_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)                

                # Aggregated Energy Fluxes (7):
                SHORTWAVE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                LONGWAVE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                SENSIBLE_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                LATENT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                GROUND_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                RAIN_FLUX_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                MELT_ENERGY_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

                # Aggregated Surface Mass Fluxes (8):
                SNOWFALL_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                RAIN_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                EVAPORATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                SUBLIMATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                CONDENSATION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                DEPOSITION_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                SURFACE_MELT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                SMB_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

                # Aggregated Subsurface Mass Fluxes (4):
                REFREEZING_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                SUSBSURFACE_MELT_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                RUNOFF_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)
                MB_AGG = np.full(aggregation_timestep_range[idx], np.nan, dtype=precision)

                # Reset result step index
                n = -1
        
        n +=1

    # ============================================================================================================================= #

    return (indY,indX, \
            _AIR_TEMPERATURE,_AIR_PRESSURE,_RELATIVE_HUMIDITY,_WIND_SPEED,_FRACTIONAL_CLOUD_COVER, \
            _SWnet,_LWnet,_SENSIBLEnet,_LATENTnet,_GROUNDnet,_RAIN_FLUX,_MELT_ENERGY, \
            _RAIN,_SNOWFALL,_EVAPORATION,_SUBLIMATION,_CONDENSATION,_DEPOSITION,_SURFACE_MELT,_SMB, \
            _REFREEZE,_SUBSURFACE_MELT,_RUNOFF,_MB, \
            _SNOW_HEIGHT,_TOTAL_HEIGHT,_SURFACE_TEMPERATURE,_SURFACE_ALBEDO,_N_LAYERS,_FIRN_TEMPERATURE,_FIRN_TEMPERATURE_CHANGE,_FIRN_FACIE, \
            _LAYER_DEPTH,_LAYER_HEIGHT,_LAYER_DENSITY,_LAYER_TEMPERATURE,_LAYER_WATER_CONTENT,_LAYER_COLD_CONTENT,_LAYER_POROSITY,_LAYER_ICE_FRACTION, \
            _LAYER_IRREDUCIBLE_WATER,_LAYER_REFREEZE,_LAYER_HYDRO_YEAR)



    