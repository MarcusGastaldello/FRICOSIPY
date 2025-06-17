
# ------------------------------------------------------------------------------------------------------------------------

import numpy as np
import math as mt
from constants import *
from parameters import *
from numba import njit

@njit
def TOA_insolation(latitude,longitude,slope,aspect,doy,hour,leap,hoy):
      """ This function calculates the unattenuated Top Of Atmosphere (TOA) insolation corrected for topographical shading & inclination.

        M. Iqbal et al. (1983)

      Input:
            latitude                WGS 84 Latitude Value of Y-Position [decimal]
            longitude               WGS 84 Longitude Value of X-Position [decimal]
            slope                   Slope Angle of Grid Cell [degrees]
            aspect                  Relative Aspect op Grid Cell [degrees]                   
            doy                     Day of year [1-366]
            hour                    Hour of day [1-24]
            leap                    Leap year boolean [True/False]     
            hoy                     Hour of year [1-8784]
           
      Outputs:
            TOA_insol               Top Of Atmosphere (TOA) Insolation (topographically corrected) [W/m^2]
            TOA_insol_flat          Top Of Atmosphere (TOA) Insolation (flat surface) [W/m^2]
            TOA_insol_norm          Top of Atmosphere (TOA) Insolation Normal to Incident Beam [W/m^2]

      """

      # ========================================== #
      # Time as a fraction of a year (in radians):   
      # ========================================== #

      time_decimal = np.where(leap,hoy/8784,hoy/8760)
      time_rad = 2 * mt.pi * time_decimal

      # ====================================================================== #
      # Top-of-Atmosphere (TOA) radiation on a surface normal to incident beam:   
      # ====================================================================== #

      TOA_insol_norm = (1353.0 * (1.0 + 0.034 * np.cos(time_rad)))

      # =============================== #
      # Solar Declination: (in radians)   
      # =============================== #

      Declination = 0.322003 - 22.971 * np.cos(time_rad) - 0.357898 * np.cos(2 * time_rad) - 0.14398 * np.cos(3 * time_rad) + 3.94638 * np.sin(time_rad) + 0.019334 * np.sin(2 * time_rad) + 0.05928 * np.sin(3 *time_rad)

      # ============================== #
      # Solar Hour Angle: (in degrees)
      # ============================== #

      Equation_of_time = 229.18 * (0.000075 + 0.001868 * np.cos(time_rad) - 0.032077 * np.sin(time_rad) - 0.014615 * np.cos(2 * time_rad) - 0.040849 * np.sin(2 * time_rad))
      Time_offset = Equation_of_time + (4 * longitude)                                    # in minutes
      Local_solar_time = hour + (Time_offset / 60)                                        # in decimal hours
      Solar_hour_angle = -(15 * (Local_solar_time - 12))                                 

      # ============================= #
      # Solar Elevation: (in radians)
      # ============================= #

      Solar_Elevation = np.arcsin(np.sin(np.radians(Declination)) * np.sin(np.radians(latitude)) + np.cos(np.radians(Declination)) * np.cos(np.radians(latitude)) * np.cos(np.radians(Solar_hour_angle)))
      Day_Binary = np.where((Solar_Elevation >= 0),1,0)   # <0 - Night / >1 - Daytime

      # ==================================================== #
      # Top-of-Atmosphere (TOA) radiation on a flat surface:   
      # ==================================================== #

      TOA_Adjustment = (((np.sin(np.radians(latitude))) * np.sin(np.radians(Declination))) + (np.cos(np.radians(latitude)) * np.cos(np.radians(Declination)) * np.cos(np.radians(Solar_hour_angle))))
      TOA_insol_flat = TOA_insol_norm * TOA_Adjustment

      # ====================================================================== #
      # Top-of-Atmosphere (TOA) radiation on an inclined surface (Iqbal 1983):   
      # ====================================================================== #

      Term_A = (np.cos(np.radians(slope)) * np.sin(np.radians(latitude)) - np.cos(np.radians(latitude)) * np.cos(np.radians(180 - aspect)) * np.sin(np.radians(slope))) * np.sin(np.radians(Declination))
      Term_B = (np.sin(np.radians(latitude)) * np.cos(np.radians(180 - aspect)) * np.sin(np.radians(slope)) + np.cos(np.radians(slope)) * np.cos(np.radians(latitude))) * np.cos(np.radians(Declination)) * np.cos(np.radians(Solar_hour_angle))
      Term_C = np.sin(np.radians(180 - aspect)) * np.sin(np.radians(slope)) * np.cos(np.radians(Declination)) * np.sin(np.radians(Solar_hour_angle))

      Inclination_correction = Term_A + Term_B + Term_C
      TOA_insol_inclined = Inclination_correction * TOA_insol_norm * Day_Binary
      TOA_insol = np.where(TOA_insol_inclined > 0,TOA_insol_inclined,0) 

      return TOA_insol,TOA_insol_flat,TOA_insol_norm

# ====================================================================================================================

@njit
def shortwave_radiation_input(PRES,T2,RH,TOA_insol,TOA_insol_flat,TOA_insol_norm,Illumination, N = None, SWin = None):

      """ This function calculates the ShortWave (SW) Radiation Input at a given time step across the entire model domain.
        (i.e. SW Input calculation is constant across the spatial domain for any given time step) --> [t,:,:] )

      Input:
            PRES:             Atmouspheric Pressure [hpa]  
            T2:               Temperature [K]
            RH:               Relative Humidity [%]
            TOA_insol         Top Of Atmosphere (TOA) Insolation (topographically corrected) [W/m^2]
            TOA_insol_flat    Top Of Atmosphere (TOA) Insolation (flat surface) [W/m^2]
            TOA_insol_norm    Top of Atmosphere (TOA) Insolation Normal to Incident Beam [W/m^2]
            Illumination      Solar Illumination Boolean [0 (shaded) or 1 (insolated)]
            N:                Fractional Cloud Cover [0-1] (Option A)
            SWin:             Shortwave Radiation Input on AWS Station (Uncorrected) [W/m^2] (Option B)
 
      Output:
            SWin              Shortwave Radiation Input [W/m^2]
      """
      
      # ===================================================== #
      # Transmissivity after Gaseous Absorption / Scattering:
      # ===================================================== #

      m = 35 * ((PRES * 100) / Atm_Pressure) * (1224 * (TOA_insol_flat / TOA_insol_norm)**2+ 1) **(-0.5)
      t_gaseous = 1.021 - 0.084 * np.sqrt(m * (949 *(PRES/10) * 1e-5 + 0.051))

      # ============================================================ #
      # Transmissivity after Water Vapor Absorption (Lawrence, 2005)
      # ============================================================ #

      tempdew_kelvin = T2 * ((1 - ( T2 * np.log(RH/100) / (lat_heat_sublimation / R_watervapour)))**(-1))
      tempdew_fahrenheit = 32.0 + 1.8 * (tempdew_kelvin - 273.15)					
      u = np.exp(0.1133 - np.log(optical_depth + 1) + 0.0393 * tempdew_fahrenheit)
      t_watervapour = 1 - 0.077 *(u * m)**0.3

      # ======================================== #
      # Transmissivity after Aerosol Absorption:
      # ======================================== #

      t_aerosol = exp_aerosol**m                                 

      # ======================= #
      # Fractional Cloud Cover:
      # ======================= #

      # Use fractional cloud cover (N) to determine SWin across grid:
      if SWin is not None:

            # Quadratic constant
            c = ((TOA_insol * t_gaseous * t_watervapour * t_aerosol) / SWin) -1

            # Solve quadratic equation:
            N = (-alpha + np.sqrt(alpha**2 - (4 * beta * c))) / 2 * beta
            
            # Ensure fractional cloud cover remains within physical bounds:
            N = np.clip(N,0,1)

      # ================================================= #
      # Transmissivity after Cloud Absorbtion/Scattering:
      # ================================================= #

      t_cloud = 1 - (alpha * N) - (beta * (N**2))      

      # ================================================= #
      # Direct, Diffuse and Total Radiation after Shading:   
      # ================================================= #

      TOA_insol_direct =  (0.2 + 0.65 * ( 1 - N )) * Illumination * TOA_insol
      TOA_insol_diffuse = (0.8 - 0.65 * (1 - N )) * TOA_insol
      TOA_combined = TOA_insol_direct + TOA_insol_diffuse

      # ========================= #
      # Incoming Solar Radiation:
      # ========================= #

      Transmissivity = t_gaseous * t_watervapour * t_aerosol *  t_cloud
      SWin = TOA_combined *  Transmissivity

      return SWin

      # ====================================================================================================================
