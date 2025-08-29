"""
    ==================================================================

                          SHORTWAVE RADIATION MODULE

        This module determines the incoming shortwave radiation by
        first calculating the Top of Atmosphere (TOA) insolation 
        and then the degree of attenuation by topographic shading
        gaseous & water vapour absorption, aerosols and cloud cover.

    ==================================================================
"""

import numpy as np
import math as mt
from constants import *
from parameters import *
from numba import njit

# ================================== #
# Top of Atmosphere (TOA) Insolation
# ================================== #

@njit
def TOA_insolation(latitude,longitude,slope,aspect,hour,leap,hoy):
    """ This function calculates the unattenuated Top Of Atmosphere (TOA) insolation corrected for topographical shading & inclination.
            after Iqbal et al. (1983)
            (adapted from the EBFM - van Pelt et al. (2012)) 

    Parameters:
                n/a
    Input:
                latitude          ::    WGS 84 Latitude Value of Y-Position [decimal]
                longitude         ::    WGS 84 Longitude Value of X-Position [decimal]
                slope             ::    Slope Angle of Grid Cell [degrees]
                aspect            ::    Relative Aspect op Grid Cell [degrees]                   
                hour              ::    Hour of day [1-24]
                leap              ::    Leap year boolean [True/False]     
                hoy               ::    Hour of year [1-8784]           
    Output:
                TOA_insol               Top Of Atmosphere (TOA) Insolation (topographically corrected) [W/m^2]
                TOA_insol_flat    ::    Top Of Atmosphere (TOA) Insolation (flat surface) [W/m^2]
                TOA_insol_norm    ::    Top of Atmosphere (TOA) Insolation Normal to Incident Beam [W/m^2]

    """

    # Time as a fraction of a year (in radians):   
    time_decimal = np.where(leap,hoy/8784,hoy/8760)
    time_rad = 2 * mt.pi * time_decimal

    # Top-of-Atmosphere (TOA) radiation on a surface normal to incident beam:   
    TOA_insol_norm = (1353.0 * (1.0 + 0.034 * np.cos(time_rad)))

    # Solar Declination: (in radians)   
    Declination = 0.322003 - 22.971 * np.cos(time_rad) - 0.357898 * np.cos(2 * time_rad) - 0.14398 * np.cos(3 * time_rad) + 3.94638 * np.sin(time_rad) + 0.019334 * np.sin(2 * time_rad) + 0.05928 * np.sin(3 *time_rad)

    # Solar Hour Angle: (in degrees)
    Equation_of_time = 229.18 * (0.000075 + 0.001868 * np.cos(time_rad) - 0.032077 * np.sin(time_rad) - 0.014615 * np.cos(2 * time_rad) - 0.040849 * np.sin(2 * time_rad))
    Time_offset = Equation_of_time + (4 * longitude)   # in minutes
    Local_solar_time = hour + (Time_offset / 60)       # in decimal hours
    Solar_hour_angle = -(15 * (Local_solar_time - 12))                                 

    # Solar Elevation: (in radians)
    Solar_Elevation = np.arcsin(np.sin(np.radians(Declination)) * np.sin(np.radians(latitude)) + np.cos(np.radians(Declination)) * np.cos(np.radians(latitude)) * np.cos(np.radians(Solar_hour_angle)))
    Day_Binary = np.where((Solar_Elevation >= 0),1,0)   # <0 - Night / >1 - Daytime

    # Top-of-Atmosphere (TOA) radiation on a flat surface:   
    TOA_Adjustment = (((np.sin(np.radians(latitude))) * np.sin(np.radians(Declination))) + (np.cos(np.radians(latitude)) * np.cos(np.radians(Declination)) * np.cos(np.radians(Solar_hour_angle))))
    TOA_insol_flat = TOA_insol_norm * TOA_Adjustment

    # Top-of-Atmosphere (TOA) radiation on an inclined surface (Iqbal 1983): 
    Inclination_correction = (np.cos(np.radians(slope)) * np.sin(np.radians(latitude)) - np.cos(np.radians(latitude)) * np.cos(np.radians(180 - aspect)) * np.sin(np.radians(slope))) * np.sin(np.radians(Declination)) + \
                             (np.sin(np.radians(latitude)) * np.cos(np.radians(180 - aspect)) * np.sin(np.radians(slope)) + np.cos(np.radians(slope)) * np.cos(np.radians(latitude))) * np.cos(np.radians(Declination)) * np.cos(np.radians(Solar_hour_angle)) + \
                             (np.sin(np.radians(180 - aspect)) * np.sin(np.radians(slope)) * np.cos(np.radians(Declination)) * np.sin(np.radians(Solar_hour_angle)))   

    TOA_insol_inclined = Inclination_correction * TOA_insol_norm * Day_Binary
    TOA_insol = np.where(TOA_insol_inclined > 0,TOA_insol_inclined,0) 

    return TOA_insol,TOA_insol_flat,TOA_insol_norm

# ====================================================================================================================

# ========================= #
# Input Shortwave Radiation
# ========================= #

@njit
def shortwave_radiation_input(PRES,T2,RH,TOA_insol,TOA_insol_flat,TOA_insol_norm,Illumination, N = None, SWin = None):
    """ This function calculates the ShortWave (SW) Radiation Input at a given time step for a single spatial node.
    after Kondratyev (1969), McDonald (1960), Houghton (1959) and Greuell (1997)
    (adapted from the EBFM - van Pelt et al. (2012)) 

    Parameters:
                alpha             ::    Cloud transmissivity coefficient [-]
                beta              ::    Cloud transmissivity coefficient [-]
    Input:
                PRES:             ::    Atmouspheric Pressure [hPa]  
                T2:               ::    Temperature [K]
                RH:               ::    Relative Humidity [%]
                TOA_insol         ::    Top Of Atmosphere (TOA) Insolation (topographically corrected) [W/m^2]
                TOA_insol_flat    ::    Top Of Atmosphere (TOA) Insolation (flat surface) [W/m^2]
                TOA_insol_norm    ::    Top of Atmosphere (TOA) Insolation Normal to Incident Beam [W/m^2]
                Illumination      ::    Solar Illumination Boolean [0 (shaded) or 1 (insolated)]
                N:                ::    Fractional Cloud Cover [0-1]
                SWin:             ::    Shortwave Radiation Input on AWS Station [W/m^2]
    Output:
                N:                ::    Fractional Cloud Cover [0-1]
                SWin              ::    Shortwave Radiation Input [W/m^2]
    """
      
    # Transmissivity after Gaseous Absorption / Scattering (Kondratyev, 1969):
    m = 35 * ((PRES * 100) / Atm_Pressure) * (1224 * (TOA_insol_flat / TOA_insol_norm)**2+ 1) **(-0.5)
    t_gaseous = 1.021 - 0.084 * np.sqrt(m * (949 *(PRES/10) * 1e-5 + 0.051))

    # Transmissivity after Water Vapor Absorption (McDonald, 1960)
    tempdew_kelvin = T2 * ((1 - ( T2 * np.log(RH/100) / (lat_heat_sublimation / R_watervapour)))**(-1))
    tempdew_fahrenheit = 32.0 + 1.8 * (tempdew_kelvin - 273.15)					
    u = np.exp(0.1133 - np.log(optical_depth + 1) + 0.0393 * tempdew_fahrenheit)
    t_watervapour = 1 - 0.077 *(u * m)**0.3

    # Transmissivity after Aerosol Absorption (Houghton, 1959):
    t_aerosol = exp_aerosol**m                                 

    # Fractional Cloud Cover:
    if SWin is not None:

        # Determine cloud transmissivity at AWS:
        t_cloud_AWS = SWin / (TOA_insol_flat * t_gaseous * t_watervapour * t_aerosol)
        t_cloud_AWS = np.minimum(t_cloud_AWS,1)

        # Quadratic coefficients:
        a = -cloud_transmissivity_coeff_beta 
        b = -cloud_transmissivity_coeff_alpha
        c = (1 - t_cloud_AWS)

        # Solve Quadratic Equation to determine fractional Cloud Cover (N):
        N = (-b - np.sqrt(b**2 - (4 * a * c))) / 2 * a

        # Ensure fractional cloud cover remains within physical bounds:
        N = np.clip(N,0,1)

    # Transmissivity after Cloud Absorbtion/Scattering (Greuell, 1997):
    t_cloud = 1 - (cloud_transmissivity_coeff_alpha * N) - (cloud_transmissivity_coeff_beta * (N**2))      

    # Direct, Diffuse and Total Radiation after Shading:   
    TOA_insol_direct =  (0.2 + 0.65 * ( 1 - N )) * Illumination * TOA_insol
    TOA_insol_diffuse = (0.8 - 0.65 * (1 - N )) * TOA_insol
    TOA_combined = TOA_insol_direct + TOA_insol_diffuse

    # Incoming Solar Radiation:
    Transmissivity = t_gaseous * t_watervapour * t_aerosol *  t_cloud
    SWin = TOA_combined *  Transmissivity

    return SWin, N

# ====================================================================================================================
