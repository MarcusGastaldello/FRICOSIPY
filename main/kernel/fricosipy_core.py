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

def fricosipy_core(STATIC, METEO, ILLUMINATION, indY, indX, nt):
    """ Cosipy core function, which perform the calculations on one core.

    Variables:
    ======
    STATIC: Xarray dataset containing topographic/static data (x,y)
    METEO: Xarray dataset containing meteoroligical data (t)
    ILLUMINATION: Xarray dataset containing solar illumination data (x,y,t)
    indY: Y index of the simulated node
    indX: X index of the simulated node
    nt : Temporal dimension of the output result dataset

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
        raise ValueError("\t Error: Either Precipitation ('RRR') or the variables of the three phase accumulation model ('ACC_ANOMALY','D','ACCUMULATION') must be supplied in the input METEO & STATIC files")

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
        raise ValueError("\t Error: Either Fractional cloud cover ('N') or incoming Longwave radiation ('LWin') must be supplied in the input METEO file")

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
    
    # ====================== #
    # LOCAL RESULT VARIABLES
    # ====================== #

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
    _SURFACE_MASS_BALANCE = np.full(nt,np.nan, dtype=precision)

    # Subsurface Mass Fluxes (4):
    _REFREEZE = np.full(nt,np.nan, dtype=precision)
    _SUBSURFACE_MELT = np.full(nt,np.nan, dtype=precision)
    _RUNOFF = np.full(nt,np.nan, dtype=precision)
    _MASS_BALANCE = np.full(nt,np.nan, dtype=precision)

    # Other Information (9):
    _SNOW_HEIGHT = np.full(nt,np.nan, dtype=precision)
    _SNOW_WATER_EQUIVALENT = np.full(nt,np.nan, dtype=precision)
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

    # ============================== #
    # AGGREGATION & OUTPUT REPORTING
    # ============================== #

    if model_spin_up == True:

        # Convert user-defined initial timestamp from datetime [ns] to timestamp index:
        initial_index = ((pd.to_datetime(initial_timestamp).to_numpy() - pd.to_datetime(time_start).to_numpy()).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)

    else: 
        # Initial index is equal to the first timestamp in the METEO dataset (0):
        initial_index = 0

    if reduced_output == True:

        # Output variables are reported on user-defined output timestamps (converting from datetime [ns] to timestamp index):
        output_indexes = ((pd.read_csv(os.path.join(data_path,'output/output_timestamps',output_timestamps), header = None).to_numpy(dtype = np.datetime64) - \
                           METEO.time[0].data).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)
        time_end_index = ((METEO.time[-1].data - METEO.time[0].data).astype(dtype = np.float64) / (1e9 * dt)).astype(dtype = np.int32)

        # Final simulation timestamp must be included in the output timestamps to prevent an error:
        if time_end_index not in output_indexes:
            output_indexes = np.append(output_indexes, time_end_index)

    else:

        # Output variables are reported on all simulation timestamps:
        output_indexes = np.arange(initial_index, initial_index + nt)

    # Aggregation timesteps for output variables between output timestamps:
    aggregation_timesteps = np.diff(np.insert(output_indexes,0,(initial_index - 1)))

    # ========= #
    # TIME LOOP
    # ========= #

    # Initial Variables:
    cumulative_melt = 0.0
    surface_temperature = 270
    Initial_Firn_Temperature = np.nan
    albedo_snow = albedo_fresh_snow

    # Indexes:
    idx_agg = 0 # Aggregation index (index of the variable aggregation arrays)
    idx_res = 0 # Result index (index of the output/result variable arrays)

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
        if RAIN<(minimum_snowfall*(density_fresh_snow/water_density) * 1000.0):
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
        if ((model_spin_up == True) and (t == initial_index)) or ((model_spin_up == False) and (t == 0)):

            # Aggregated Meteorological Data (5):
            AIR_TEMPERATURE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            AIR_PRESSURE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            RELATIVE_HUMIDITY_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            WIND_SPEED_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            FRACTIONAL_CLOUD_COVER_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

            # Aggregated Energy Fluxes (7):
            SHORTWAVE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            LONGWAVE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SENSIBLE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            LATENT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            GROUND_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            RAIN_FLUX_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            MELT_ENERGY_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

            # Aggregated Surface Mass Fluxes (8):
            RAIN_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SNOWFALL_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            EVAPORATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SUBLIMATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            CONDENSATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            DEPOSITION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SURFACE_MELT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SURFACE_MASS_BALANCE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

            # Aggregated Subsurface Mass Fluxes (4):
            REFREEZING_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            SUSBSURFACE_MELT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            RUNOFF_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
            MASS_BALANCE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

            # Reset result step index
            idx_agg = 0

            # Calculate initial firn temperature
            Index_Depth = np.searchsorted(GRID.get_depth(), firn_temperature_depth, side="left")   
            Initial_Firn_Temperature = GRID.get_temperature()[Index_Depth] - 273.16

        # ================ #
        # DATA AGGREGATION
        # ================ #

        # Store Aggregated Variables:
        if ((model_spin_up == True) and (t >= initial_index)) or (model_spin_up == False):

            # Aggregated Meteorological Data (5):
            AIR_TEMPERATURE_AGG[idx_agg] = T2[t]
            AIR_PRESSURE_AGG[idx_agg] = PRES[t]
            RELATIVE_HUMIDITY_AGG[idx_agg] = RH2[t]
            WIND_SPEED_AGG[idx_agg] = U2[t]
            FRACTIONAL_CLOUD_COVER_AGG[idx_agg] = N[t]

            # Aggregated Energy Fluxes (7):
            SHORTWAVE_AGG[idx_agg] = sw_radiation_net
            LONGWAVE_AGG[idx_agg] = lw_radiation_in + lw_radiation_out
            SENSIBLE_AGG[idx_agg] = sensible_heat_flux
            LATENT_AGG[idx_agg] = latent_heat_flux
            GROUND_AGG[idx_agg] = ground_heat_flux
            RAIN_FLUX_AGG[idx_agg] = rain_heat_flux
            MELT_ENERGY_AGG[idx_agg] = melt_energy

            # Aggregated Surface Mass Fluxes (8):
            RAIN_AGG[idx_agg] = RAIN / 1000
            SNOWFALL_AGG[idx_agg] = SNOWFALL * (density_fresh_snow/water_density)
            EVAPORATION_AGG[idx_agg] = evaporation
            SUBLIMATION_AGG[idx_agg] = sublimation
            CONDENSATION_AGG[idx_agg] = condensation
            DEPOSITION_AGG[idx_agg] = deposition
            SURFACE_MELT_AGG[idx_agg] = surface_melt
            SURFACE_MASS_BALANCE_AGG[idx_agg] = surface_mass_balance

            # Aggregated Subsurface Mass Fluxes (4):
            REFREEZING_AGG[idx_agg] = water_refrozen
            SUSBSURFACE_MELT_AGG[idx_agg] = subsurface_melt
            RUNOFF_AGG[idx_agg] = Q
            MASS_BALANCE_AGG[idx_agg] = mass_balance 

            # Note: other variables are instantaneously reported and not aggregated!

            # Increase aggregation index:
            idx_agg += 1  

        # ============== #
        # RESULT WRITING
        # ============== #

        if (t in output_indexes):

            # Aggregated Meteorological Data (5):
            _AIR_TEMPERATURE[idx_res] = AIR_TEMPERATURE_AGG.mean()
            _AIR_PRESSURE[idx_res] = AIR_PRESSURE_AGG.mean()
            _RELATIVE_HUMIDITY[idx_res] = RELATIVE_HUMIDITY_AGG.mean()
            _WIND_SPEED[idx_res] = WIND_SPEED_AGG.mean()
            _FRACTIONAL_CLOUD_COVER[idx_res] = FRACTIONAL_CLOUD_COVER_AGG.mean()

            # Surface Energy Fluxes (Average Aggregated) (7):
            _SWnet[idx_res] = SHORTWAVE_AGG.mean()
            _LWnet[idx_res] = LONGWAVE_AGG.mean()
            _SENSIBLEnet[idx_res] = SENSIBLE_AGG.mean()
            _LATENTnet[idx_res] = LATENT_AGG.mean()
            _GROUNDnet[idx_res] = GROUND_AGG.mean()
            _RAIN_FLUX[idx_res] = RAIN_FLUX_AGG.mean()
            _MELT_ENERGY[idx_res] = MELT_ENERGY_AGG.mean()

            # Surface Mass Fluxes (Cumulative Aggregated) (8):
            _RAIN[idx_res] = RAIN_AGG.sum()
            _SNOWFALL[idx_res] = SNOWFALL_AGG.sum()
            _EVAPORATION[idx_res] = EVAPORATION_AGG.sum()
            _SUBLIMATION[idx_res] = SUBLIMATION_AGG.sum()
            _CONDENSATION[idx_res] = CONDENSATION_AGG.sum()
            _DEPOSITION[idx_res] = DEPOSITION_AGG.sum()
            _SURFACE_MELT[idx_res] = SURFACE_MELT_AGG.sum()
            _SURFACE_MASS_BALANCE[idx_res] = SURFACE_MASS_BALANCE_AGG.sum()

            # Subsurface Mass Fluxes (Cumulative Aggregated) (4):
            _REFREEZE[idx_res] = REFREEZING_AGG.sum()
            _SUBSURFACE_MELT[idx_res] = SUSBSURFACE_MELT_AGG.sum()
            _RUNOFF[idx_res] = RUNOFF_AGG.sum()
            _MASS_BALANCE[idx_res] = MASS_BALANCE_AGG.sum()

            # Other Information (Instantaneous) (9):
            _SNOW_HEIGHT[idx_res] = GRID.get_total_snowheight()
            _SNOW_WATER_EQUIVALENT[idx_res] = np.sum(np.asarray(GRID.get_snow_heights()) * (np.asarray(GRID.get_snow_densities()) / water_density))
            _TOTAL_HEIGHT[idx_res] = GRID.get_total_height()
            _SURFACE_TEMPERATURE[idx_res] = surface_temperature
            _SURFACE_ALBEDO[idx_res] = albedo
            _N_LAYERS[idx_res] = GRID.get_number_layers()

            # Calculate Firn temperatures:
            Index_Depth = np.searchsorted(GRID.get_depth(), firn_temperature_depth, side="left")
            _FIRN_TEMPERATURE[idx_res] = GRID.get_temperature()[Index_Depth] - zero_temperature
            _FIRN_TEMPERATURE_CHANGE[idx_res] = _FIRN_TEMPERATURE[idx_res] - Initial_Firn_Temperature

            # Determine Firn Facie:
            if GRID.get_temperature()[Index_Depth] - zero_temperature > 0.1:
                _FIRN_FACIE[idx_res] = 4
            elif cumulative_melt == 0:
                _FIRN_FACIE[idx_res] = 1
            elif not np.any(GRID.get_firn_refreeze()):
                _FIRN_FACIE[idx_res] = 2
            else:
                _FIRN_FACIE[idx_res] = 3

            # Subsurface Variables (Instantaneous) (11):
            if full_field:
                if GRID.get_number_layers() > max_layers:
                    _LAYER_DEPTH[idx_res, 0:max_layers] = GRID.get_depth()[0:max_layers]
                    _LAYER_HEIGHT[idx_res, 0:max_layers] = GRID.get_height()[0:max_layers]
                    _LAYER_DENSITY[idx_res, 0:max_layers] = GRID.get_density()[0:max_layers]
                    _LAYER_TEMPERATURE[idx_res, 0:max_layers] = GRID.get_temperature()[0:max_layers]
                    _LAYER_WATER_CONTENT[idx_res, 0:max_layers] = GRID.get_liquid_water_content()[0:max_layers]
                    _LAYER_COLD_CONTENT[idx_res, 0:max_layers] = GRID.get_cold_content()[0:max_layers]
                    _LAYER_POROSITY[idx_res, 0:max_layers] = GRID.get_porosity()[0:max_layers]
                    _LAYER_ICE_FRACTION[idx_res, 0:max_layers] = GRID.get_ice_fraction()[0:max_layers]
                    _LAYER_IRREDUCIBLE_WATER[idx_res, 0:max_layers] = GRID.get_irreducible_water_content()[0:max_layers]
                    _LAYER_REFREEZE[idx_res, 0:max_layers] = GRID.get_refreeze()[0:max_layers]
                    _LAYER_HYDRO_YEAR[idx_res, 0:max_layers] = GRID.get_hydro_year()[0:max_layers]
                else:
                    _LAYER_DEPTH[idx_res, 0:GRID.get_number_layers()] = GRID.get_depth()
                    _LAYER_HEIGHT[idx_res, 0:GRID.get_number_layers()] = GRID.get_height()
                    _LAYER_DENSITY[idx_res, 0:GRID.get_number_layers()] = GRID.get_density()
                    _LAYER_TEMPERATURE[idx_res, 0:GRID.get_number_layers()] = GRID.get_temperature()
                    _LAYER_WATER_CONTENT[idx_res, 0:GRID.get_number_layers()] = GRID.get_liquid_water_content()
                    _LAYER_COLD_CONTENT[idx_res, 0:GRID.get_number_layers()] = GRID.get_cold_content()
                    _LAYER_POROSITY[idx_res, 0:GRID.get_number_layers()] = GRID.get_porosity()
                    _LAYER_ICE_FRACTION[idx_res, 0:GRID.get_number_layers()] = GRID.get_ice_fraction()
                    _LAYER_IRREDUCIBLE_WATER[idx_res, 0:GRID.get_number_layers()] = GRID.get_irreducible_water_content()
                    _LAYER_REFREEZE[idx_res, 0:GRID.get_number_layers()] = GRID.get_refreeze()
                    _LAYER_HYDRO_YEAR[idx_res, 0:GRID.get_number_layers()] = GRID.get_hydro_year()
        
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
            idx_res += 1

            # Reset Aggregation Arrays:
            if idx_res < nt:

                # Aggregated Meteorological Data (5):
                AIR_TEMPERATURE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                AIR_PRESSURE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                RELATIVE_HUMIDITY_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                WIND_SPEED_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                FRACTIONAL_CLOUD_COVER_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)                

                # Aggregated Energy Fluxes (7):
                SHORTWAVE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                LONGWAVE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                SENSIBLE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                LATENT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                GROUND_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                RAIN_FLUX_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                MELT_ENERGY_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

                # Aggregated Surface Mass Fluxes (8):
                SNOWFALL_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                RAIN_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                EVAPORATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                SUBLIMATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                CONDENSATION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                DEPOSITION_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                SURFACE_MELT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                SURFACE_MASS_BALANCE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

                # Aggregated Subsurface Mass Fluxes (4):
                REFREEZING_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                SUSBSURFACE_MELT_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                RUNOFF_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)
                MASS_BALANCE_AGG = np.full(aggregation_timesteps[idx_res], np.nan, dtype=precision)

                # Reset aggregation index
                idx_agg = 0
            

    # ============================================================================================================================= #

    return (indY,indX, \
            _AIR_TEMPERATURE,_AIR_PRESSURE,_RELATIVE_HUMIDITY,_WIND_SPEED,_FRACTIONAL_CLOUD_COVER, \
            _SWnet,_LWnet,_SENSIBLEnet,_LATENTnet,_GROUNDnet,_RAIN_FLUX,_MELT_ENERGY, \
            _RAIN,_SNOWFALL,_EVAPORATION,_SUBLIMATION,_CONDENSATION,_DEPOSITION,_SURFACE_MELT,_SURFACE_MASS_BALANCE, \
            _REFREEZE,_SUBSURFACE_MELT,_RUNOFF,_MASS_BALANCE, \
            _SNOW_HEIGHT,_SNOW_WATER_EQUIVALENT,_TOTAL_HEIGHT,_SURFACE_TEMPERATURE,_SURFACE_ALBEDO,_N_LAYERS,_FIRN_TEMPERATURE,_FIRN_TEMPERATURE_CHANGE,_FIRN_FACIE, \
            _LAYER_DEPTH,_LAYER_HEIGHT,_LAYER_DENSITY,_LAYER_TEMPERATURE,_LAYER_WATER_CONTENT,_LAYER_COLD_CONTENT,_LAYER_POROSITY,_LAYER_ICE_FRACTION, \
            _LAYER_IRREDUCIBLE_WATER,_LAYER_REFREEZE,_LAYER_HYDRO_YEAR)



    