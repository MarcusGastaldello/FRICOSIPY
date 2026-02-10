"""
    ==================================================================

                          SURFACE TEMPERATURE MODULE

        This module determines the skin-layer surface temperature 
        by iteratively equilibriating the surface energy fluxes for
        a single model timestep.

    ==================================================================
"""

import numpy as np
from constants import *
from parameters import *
from scipy.optimize import minimize, newton
from numba import njit
from types import SimpleNamespace

# ========================== #
# Surface Temperature Solver
# ========================== #

def update_surface_temperature(GRID, z0, T2, RH2, PRES, SWnet, U2, RAIN, SLOPE, N = None, LWinput = None):
    """ This module updates the surface temperature and returns the surface energy fluxes

    Parameters:

    subsurface_interpolation_depth_1    ::    First depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m]
    subsurface_interpolation_depth_2    ::    Second depth for temperature interpolation which is used for calculation of subsurface/ground heat flux [m]
    LW_emission_constant                ::    Constant in the longwave emission formula [-]

    Input:
                GRID         ::    Subsurface GRID variables -->
                z0           ::    Surface roughness [m]
                T2           ::    Air temperature [K]
                RH2          ::    Relative humidity [%]
                PRES         ::    Air pressure [hPa]
                SWnet        ::    Net shortwave radiation [W m-2]
                U2           ::    Wind velocity [m s-1]
                RAIN         ::    Rain [mm]
                SLOPE        ::    Slope of the surface [degree]
                N            ::    Fractional cloud cover [-]        
                LWinput      ::    Incoming longwave radiation [W m-2] (as input data)

    Output:
                T0           ::    Surface temperature [K]
                LWin         ::    Incoming longwave radiation [W m-2]
                LWout        ::    Outgoing longwave radiation [W m-2]
                SENSIBLE     ::    Sensible heat flux [W m-2]
                LATENT       ::    Latent heat flux [W m-2]
                GROUND       ::    Ground heat flux [W m-2]
                RAIN_HEAT    ::    Rain heat flux [W m-2]
        
    """
    
    # Interpolate subsurface temperatures to selected subsurface depths for subsurface / ground heat flux computation:
    Tz = interpolate_Tz(GRID) if GRID.get_number_layers() > 1 else (0,0)

    # Inital bounds:
    lower_bound = 220
    upper_bound = 330
    initial_guess = float(min(GRID.get_node_temperature(0), 270))

    # Determine surface temperature by equalising the energy balance (SWnet + LWnet + LATENT + SENSIBLE + GROUND + RAIN_HEAT = 0)
    surface_temperature_methods_allowed = ['L-BFGS-B','SLSQP','Newton']

    # ========================================================================================================== #
    # Limited Broyden-Fletcher-Goldfarb-Shanno (L-BFGS-B) / Sequential Least Squares Programming (SLSQP) methods
    # ========================================================================================================== #

    if surface_temperature_solver == 'L-BFGS-B' or surface_temperature_solver == 'SLSQP':
        res = minimize(energy_balance_optimisation, initial_guess, method = surface_temperature_solver,
                       bounds = ((lower_bound, upper_bound),), tol = 1e-2,
                       args = (GRID, z0, T2, RH2, PRES, SWnet, U2, RAIN, SLOPE, Tz, LWinput, N))

    # -------------------------------------------------------------------------------------------------------------------- #

    # ===================== #
    # Newton-Raphson method
    # ===================== #

    elif surface_temperature_solver == 'Newton':
        try:
            res = newton(energy_balance_optimisation, np.array([GRID.get_node_temperature(0)]), tol = 1e-2, maxiter = 50,
                        args = (GRID, z0, T2, RH2, PRES, SWnet, U2, RAIN, SLOPE, Tz, LWinput, N))
            if res < lower_bound:
                raise ValueError("Error: Surface temperature is out of physical bounds.")
            res = SimpleNamespace(**{'x':min(np.array([zero_temperature]),res),'fun':None})
	    
        except (RuntimeError,ValueError):
             # Workaround for non-convergence and unboundedness (revert to SLSQP)
             res = minimize(energy_balance_optimisation, initial_guess, method='SLSQP',
                       bounds=((lower_bound, upper_bound),),tol=1e-2,
                       args=(GRID, z0, T2, RH2, PRES, SWnet, U2, RAIN, SLOPE, Tz, LWinput, N))
    else:
        raise ValueError("Surface temperature method = \"{:s}\" is not allowed, must be one of {:s}".format(surface_temperature_solver, ", ".join(surface_temperature_methods_allowed)))
    
    # -------------------------------------------------------------------------------------------------------------------- #

    # Set surface temperature (T0):
    T0 = min(zero_temperature,float(res.x))
    GRID.set_node_temperature(0, T0)
 
    # Determine the surface energy fluxes:
    (LWin, LWout, SENSIBLE, LATENT, GROUND, RAIN_HEAT) = energy_balance_fluxes(GRID, T0, z0, T2, RH2, PRES, U2, RAIN, SLOPE, Tz, LWinput, N,)
     
    # Consistency check:
    if (T0 > zero_temperature) or (T0 < lower_bound):
        raise ValueError("Error: Surface temperature is out of physical bounds.")

    # Return surface energy fluxes:
    return res.fun, T0, LWin, LWout, SENSIBLE, LATENT, GROUND, RAIN_HEAT

# ====================================================================================================================

@njit
def energy_balance_optimisation(T0, GRID, z0, T2, RH2, PRES, SWnet, U2, RAIN, SLOPE, Tz, LWinput = None, N = None):
    """ Optimisation function to resolve the surface temperature (T0) """

    # Determine the surface energy fluxes for a given surface temperature (T0):
    (LWin, LWout, SENSIBLE, LATENT, GROUND, RAIN_HEAT) = energy_balance_fluxes(GRID, T0, z0, T2, RH2, PRES, U2, RAIN, SLOPE, Tz, LWinput, N)

    # Return the minimised residual:
    if surface_temperature_solver == 'Newton':
        return (SWnet + LWin + LWout + SENSIBLE + LATENT + GROUND + RAIN_HEAT)
    else:
        return np.abs(SWnet + LWin + LWout + SENSIBLE + LATENT + GROUND + RAIN_HEAT)
    
# ====================================================================================================================

# ===================== #
# Surface Energy Fluxes
# ===================== #

@njit
def energy_balance_fluxes(GRID, T0, z0, T2, RH2, PRES, U2, RAIN, SLOPE, Tz, LWinput = None, N = None):
    """ This functions returns the surface energy fluxes from a given estimate for the surface temperature (T0)

    Input:
                GRID         ::    Subsurface GRID variables -->
                T0           ::    Surface temperature [K]
                z0           ::    Roughness length [m]
                T2           ::    Air temperature [K]
                RH2          ::    Relative humidity [%]
                PRES         ::    Air pressure [hPa]
                U2           ::    Wind velocity [m s-1]
                RAIN         ::    RAIN [mm]
                SLOPE        ::    Slope of the surface [degree]
                LWinput      ::    Incoming longwave radiation [W m-2] (as input)
                N            ::    Fractional cloud cover [-]

    Output:
                LWin         ::    Incoming longwave radiation [W m-2]
                LWout        ::    Outgoing longwave radiation [W m-2]
                SENSIBLE     ::    Sensible heat flux [W m-2]
                LATENT       ::    Latent heat flux [W m-2]
                GROUND       ::    Ground heat flux [W m-2]
                RAIN_HEAT    ::    Rain heat flux [W m-2]
    
    """
    
    # ================ #
    # Turbluent Fluxes
    # ================ #

    # Ensure surface temperature is a scalar value (Numba compatabilitiy):
    T0 = np.asarray(T0).flat[0]

    # Saturation vapour pressure [Pa]:
    saturation_vapour_pressure_methods_allowed = ['Sonntag90']

    if saturation_vapour_pressure_method == 'Sonntag90':
        VPsat2 = method_Sonntag(T2)
        VPsat0 = method_Sonntag(T0)
    else:
        raise ValueError("Saturation water vapour method = \"{:s}\" is not allowed, must be one of {:s}".format(saturation_vapour_pressure_method, ", ".join(saturation_vapour_pressure_methods_allowed)))
    
    # Latent heat of transformation:
    if T0 >= zero_temperature:
        L = latent_heat_vaporisation
    else:
        L = latent_heat_sublimation

    # Mixing Ratio (q) at surface and at measurement height:
    q2 = (RH2   * 0.622 * (VPsat2 / (PRES - VPsat2))) / 100.0
    q0 = (100.0 * 0.622 * (VPsat0 / (PRES - VPsat0))) / 100.0

    # Dry air density:
    rho = (PRES * 100.0) / (287.058 * T2)

    # Tubulent exchange coefficient (neutral conditions):
    C_hn = 0.16 * np.power((np.log(z / z0)), -2) 
    fz = 0.25 * np.power((z0 / z), 0.5)

    # Bulk Richardson number (Ri):
    Ri = 0
    if (U2!=0):
        Ri = ((9.81 * z / np.power(U2,2)) * (((T2 - T0)/T2) + ((q2 - q0)/(q2 + (0.622 / (1 - 0.622)))))).item()

    # Stability function:
    psi = 1
    if Ri >= 0:
        psi = (np.power((1 + (10 * Ri)),-1)).item()
    elif Ri < 0:
        psi = (1 - ((10 * Ri) * np.power((1 + ((10 * C_hn) * (np.sqrt(-Ri) / fz))),-1))).item()

    # Tubulent exchange coefficient:
    C_te = C_hn * psi

    # Sensible heat flux:
    SENSIBLE = rho * specific_heat_air * C_te * U2 * (T2 - T0) * np.cos(np.radians(SLOPE))
        
    # Latent heat flux:
    LATENT = rho * L * C_te * U2 * (q2 - q0) * np.cos(np.radians(SLOPE))

    # -------------------------------------------------------------------------------------------------------------------- #

    # ======================= #
    # Longwave Radiation Flux
    # ======================= #

    # Calculate incoming longwave radiation from fractional cloud cover using the method of Konzelmann et al. 1994:
    if (LWinput is None) and (N is not None):
        VP = (RH2 * VPsat2) / 100.0
        emissivity_clear_sky = 0.23 + LW_emission_constant * np.power(100 * VP / T2, 1.0 / 8.0)
        emissivity = emissivity_clear_sky * (1 - np.power(N, 2)) + cloud_emissivity * np.power(N, 2)
        LWin = emissivity * sigma * np.power(T2, 4.0)
    
    # Otherwise, use longwave radiation data from the input meteorological data
    else:
        LWin = LWinput

    # Calculate outgoing longwave radiation.
    LWout = -surface_emission_coeff * sigma * np.power(T0, 4.0)

    # -------------------------------------------------------------------------------------------------------------------- #

    # ======================================== #
    # Ground Heat / Subsurface Conduction Flux
    # ======================================== #

    # Get thermal conductivity:
    k = GRID.get_node_thermal_conductivity(0)
	
    # Calculate ground / subsurface conduction flux using linear interpolation:
    if GRID.get_number_layers() > 1:
        x1 = subsurface_interpolation_depth_1
        x2 = subsurface_interpolation_depth_2 - subsurface_interpolation_depth_1
        Tz1, Tz2 = Tz
        GROUND = k * ((x1 / (x2 + x1)) * ((Tz2 - Tz1) / x2) + (x2 / (x2 + x1)) * ((Tz1 - T0) / x1))

	# Otherwise, if there is only a single subsurface layer:
    else:
        GROUND = k * (GRID.get_node_temperature(0) - T0) / (0.5 *  GRID.get_node_height(0))

    # -------------------------------------------------------------------------------------------------------------------- #

    # ============== #
    # Rain Heat Flux
    # ============== #

    RAIN_HEAT = water_density * specific_heat_water * (RAIN / 1000 / dt) * (T2 - T0)

    # -------------------------------------------------------------------------------------------------------------------- #

    return (LWin.item(), LWout.item(), SENSIBLE.item(), LATENT.item(), GROUND.item(), RAIN_HEAT.item())

# ==================================================================================================================== # 

# ============================================================= #
# Interpolate Temperatures for Subsurface Heat Flux Computation
# ============================================================= #

@njit
def interpolate_Tz(GRID):
    """ Interpolate subsurface temperature to depths used for the subsurface / ground heat flux computation """
    
    # Retrieve subsurface layer properties:
    z = np.asarray(GRID.get_depth())
    T = np.asarray(GRID.get_temperature())
    n = GRID.get_number_layers()

    def interpolate(target_z):

		# Skip the first node if the fresh snow layer is too thin (< 2cm)
        start_idx = 1 if z[0] < 0.02 else 0
		
        # Determine the closest subsurface node index:
        idx_1 = np.abs(z[start_idx:] - target_z).argmin() + start_idx

        # Determine the adjacent subsurface node index that bounds the target depth: 
        idx_2 = max(start_idx, idx_1 - 1) if z[idx_1] > target_z else min(n - 1, idx_1 + 1)

        # Linearly interpolate the target subsurface temperature (ensuring no division by zero error):
        dz = z[idx_1] - z[idx_2]
        Tz = T[idx_1] if dz == 0 else T[idx_1] + (T[idx_1] - T[idx_2]) / dz * (target_z - z[idx_1])  
        return Tz
    
    # Determine subsurface temperatures using linear interpolation:
    Tz1 = interpolate(subsurface_interpolation_depth_1)
    Tz2 = interpolate(subsurface_interpolation_depth_2)

    return (float(Tz1), float(Tz2))
    
# ==================================================================================================================== #

# ========================= #
# Saturated Vapour Pressure
# ========================= #

@njit
def method_Sonntag(T):
    """ Saturated vapour pressure after Sonntag (1994)
    
    Input:
                T        ::    Air or surface temperature [K]

    Output:
                VPsat    ::    Saturated vapour pressure [hPa]
    """

    if T >= 273.16:
        VPsat = 6.112 * np.exp((17.67 * (T - 273.16)) / ((T - 29.66))) # VPsat over water
    else:
        VPsat = 6.112 * np.exp((22.46 * (T - 273.16)) / ((T - 0.55)))  # VPsat over ice
    return VPsat


# ==================================================================================================================== #




