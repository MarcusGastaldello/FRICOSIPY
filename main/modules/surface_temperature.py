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

def update_surface_temperature(GRID, dt, z, z0, T2, rH2, p, SWnet, u2, RAIN, SLOPE, N = None, LWin = None):
    """ This module updates the surface temperature and returns the surface energy fluxes

    Input:

        GRID    ::    Grid structure
	    dt      ::    Integration time [s]
	    z       ::    Measurement height [m]
        z0      ::    Surface roughness [m]
        T2      ::    Air temperature [K]
        rH2     ::    Relative humidity [%]
        p       ::    Air pressure [hPa]
        SWnet   ::    Net shortwave radiation [W m-2]
        u2      ::    Wind velocity [m s-1]
        RAIN    ::    RAIN [mm]
        SLOPE   ::    Slope of the surface [degree]
        N       ::    Fractional cloud cover [-]        
        LWin    ::    Incoming longwave radiation [W m-2]

    Output:

        T0      ::    Surface temperature [K]
        Li      ::    Incoming longwave radiation [W m-2]
        Lo      ::    Outgoing longwave radiation [W m-2]
        H       ::    Sensible heat flux [W m-2]
        L       ::    Latent heat flux [W m-2]
        B       ::    Ground heat flux [W m-2]
        Qrr     ::    Rain heat flux [W m-2]
        rho     ::    Air density [kg m-3]
        Lv      ::    Latent heat of vaporization [J kg-1]
	    MOL     ::    Monin-Obukhov length
        Cs_t    ::    Stanton number [-]
        Cs_q    ::    Dalton number [-]
        q0      ::    Mixing ratio at the surface [kg kg-1]
        q2      ::    Mixing ratio at measurement height [kg kg-1]
        
    """
    
    #Interpolate subsurface temperatures to selected subsurface depths for GHF computation
    B_Ts = interp_subT(GRID)

    #Update surface temperature
    lower_bnd_ts = 220
    upper_bnd_ts = 330
    initial_guess = min(GRID.get_node_temperature(0),270)
    
    if sfc_temperature_method == 'L-BFGS-B' or sfc_temperature_method == 'SLSQP':
        # Get surface temperature by minimizing the energy balance function (SWnet+Li+Lo+H+L=0)
        res = minimize(eb_optim, initial_guess, method=sfc_temperature_method,
                       bounds=((lower_bnd_ts, upper_bnd_ts),),tol=1e-2,
                       args=(GRID, dt, z, z0, T2, rH2, p, SWnet, u2, RAIN, SLOPE, B_Ts, LWin, N))
		       
    elif sfc_temperature_method == 'Newton':
        try:
            res = newton(eb_optim, np.array([GRID.get_node_temperature(0)]), tol=1e-2, maxiter=50,
                        args=(GRID, dt, z, z0, T2, rH2, p, SWnet, u2, RAIN, SLOPE, B_Ts, LWin, N))
            if res < lower_bnd_ts:
                raise ValueError("TS Solution is out of bounds")
            res = SimpleNamespace(**{'x':min(np.array([zero_temperature]),res),'fun':None})
	    
        except (RuntimeError,ValueError):
             #Workaround for non-convergence and unboundedness
             res = minimize(eb_optim, initial_guess, method='SLSQP',
                       bounds=((lower_bnd_ts, upper_bnd_ts),),tol=1e-2,
                       args=(GRID, dt, z, z0, T2, rH2, p, SWnet, u2, RAIN, SLOPE, B_Ts, LWin, N))
    else:
        print('Invalid method for minimizing the residual')

    # Set surface temperature
    surface_temperature = min(zero_temperature,float(res.x))
    GRID.set_node_temperature(0,surface_temperature)
 
    (Li, Lo, H, L, B, Qrr, rho, Lv, MOL, Cs_t, Cs_q, q0, q2) = eb_fluxes(GRID, surface_temperature, dt, 
                                                             z, z0, T2, rH2, p, u2, RAIN, SLOPE, 
                                                             B_Ts, LWin, N,)
     
    # Consistency check
    if (surface_temperature > zero_temperature) or (surface_temperature < lower_bnd_ts):
        print('Surface temperature is outside bounds:',GRID.get_node_temperature(0))

    # Return fluxes
    return res.fun, surface_temperature, Li, Lo, H, L, B, Qrr, rho, Lv, MOL, Cs_t, Cs_q, q0, q2

@njit
def eb_optim(T0, GRID, dt, z, z0, T2, rH2, p, SWnet, u2, RAIN, SLOPE, B_Ts, LWin=None, N=None):
    ''' Optimization function to solve for surface temperature T0 '''

    # Get surface fluxes for surface temperature T0
    (Li,Lo,H,L,B,Qrr,rho,Lv,MOL,Cs_t,Cs_q,q0,q2) = eb_fluxes(GRID, T0, dt, z, z0, T2, rH2, p, u2, RAIN, SLOPE, B_Ts, LWin, N)

    # Return the residual (is minimized by the optimization function)
    if sfc_temperature_method == 'Newton':
        return (SWnet+Li+Lo+H+L+B+Qrr)
    else:
        return np.abs(SWnet+Li+Lo+H+L+B+Qrr)
    
# ====================================================================================================================

# ===================== #
# Surface Energy Fluxes
# ===================== #

@njit
def eb_fluxes(GRID, T0, dt, z, z0, T2, rH2, p, u2, RAIN, SLOPE, B_Ts, LWin = None, N = None):
    """ This functions returns the surface fluxes 

    Given:

        GRID    ::    Grid structure
        T0      ::    Surface temperature [K]
        dt      ::    Integration time [s]
	    z       ::    Measurement height [m]
        z0      ::    Roughness length [m]
        T2      ::    Air temperature [K]
        rH2     ::    Relative humidity [%]
        p       ::    Air pressure [hPa]
        u2      ::    Wind velocity [m s-1]
        RAIN    ::    RAIN (mm)
        SLOPE   ::    Slope of the surface [degree]
        LWin    ::    Incoming longwave radiation [W m-2]
        N       ::    Fractional cloud cover [-]

    Returns:

        Li      ::    Incoming longwave radiation [W m-2]
        Lo      ::    Outgoing longwave radiation [W m-2]
        H       ::    Sensible heat flux [W m-2]
        L       ::    Latent heat flux [W m-2]
        B       ::    Ground heat flux [W m-2]
        Qrr     ::    Rain heat flux [W m-2]
        rho     ::    Air density [kg m-3]
        Lv      ::    Latent heat of vaporization [J kg-1]
	    MOL     ::    Monin Obhukov length
        Cs_t    ::    Stanton number [-]
        Cs_q    ::    Dalton number [-]
        q0      ::    Mixing ratio at the surface [kg kg-1]
        q2      ::    Mixing ratio at measurement height [kg kg-1]
    
    """
    
    # ================ #
    # Turbluent Fluxes
    # ================ #

    # Saturation vapour pressure (hPa)
    if saturation_water_vapour_method == 'Sonntag90':
        Ew = method_EW_Sonntag(T2)
        Ew0 = method_EW_Sonntag(T0)
    else:
        print('Method for saturation water vapour ', saturation_water_vapour_method, ' not available, using default')
        Ew = method_EW_Sonntag(T2)
        Ew0 = method_EW_Sonntag(T0)
    
    # latent heat of vaporization
    if T0 >= zero_temperature:
        Lv = lat_heat_vaporize
    else:
        Lv = lat_heat_sublimation

    # Water vapour at height z in  m (hPa)
    Ea = (rH2 * Ew) / 100.0

    # Calc incoming longwave radiation, if not available Ea has to be in Pa (Konzelmann 1994)
    # numba has no implementation for power(none, int)
    if (LWin is None) and (N is not None):
        eps_cs = 0.23 + LW_emission_constant * np.power(100*Ea/T2,1.0/8.0)
        eps_tot = eps_cs * (1 - np.power(N,2)) + cloud_emissivity * np.power(N,2)
        Li = eps_tot * sigma * np.power(T2,4.0)
    else:
    # otherwise use LW data from file
        Li = LWin

    # turbulent Prandtl number
    Pr = 0.8

    # Mixing Ratio at surface and at measurement height  or calculate with other formula? 0.622*e/p = q
    q2 = (rH2 * 0.622 * (Ew / (p - Ew))) / 100.0
    q0 = (100.0 * 0.622 * (Ew0 / (p - Ew0))) / 100.0

    # -------------------------------------------------------------------------------------------------------------------- #
    
    if turbulent_fluxes_method == 'default':

        # ============== #
        # Default Method
        # ============== #

        # Moist Air density 
        rho = (p*100.0) / (287.058 * (T2 * (1 + 0.608 * q2)))
        
        # Bulk transfer coefficient 
        z0t = z0/100    # Roughness length for sensible heat
        z0q = z0/10     # Roughness length for moisture
        L = None

        # Monin-Obukhov stability correction
        if stability_correction == 'MO':
            L = 0.0
            H0 = T0*0. + np.inf		#numba: consistent typing of H0
            diff = np.inf
            optim = True
            niter = 0

            # Optimize Obukhov length
            while optim:
                # ustar with initial condition of L == x
                ust = ustar(u2,z,z0,L)
        
                # Sensible heat flux for neutral conditions
                Cd = np.power(0.41,2.0) / np.power(np.log(z/z0) - phi_m(z,L) - phi_m(z0,L),2.0)
                Cs_t = 0.41*np.sqrt(Cd) / (np.log(z/z0t) - phi_tq(z,L) - phi_tq(z0,L))
                Cs_q = 0.41*np.sqrt(Cd) / (np.log(z/z0q) - phi_tq(z,L) - phi_tq(z0,L))
        
                # Surface heat flux
                H = rho * spec_heat_air * Cs_t * u2 * (T2-T0) * np.cos(np.radians(SLOPE))
        
                # Latent heat flux
                LE = rho * Lv * Cs_q * u2 * (q2-q0) *  np.cos(np.radians(SLOPE))
        
                # Monin-Obukhov length
                L = MO(rho, ust, T2, H)
	    
                # Heat flux differences between iterations
                diff = np.abs(H0-H)
           
                # Termination criterion
                if (diff<1e-1) | (niter>5):
                    optim = False
                niter = niter+1
            
                # Store last heat flux in H0
                H0 = H
  
        # Richardson-Number stability correction
        elif stability_correction == 'Ri':
            # Bulk transfer coefficient 
            Cs_t = np.power(0.41,2.0) / ( np.log(z/z0) * np.log(z/z0t) )    # Stanton-Number
            Cs_q = np.power(0.41,2.0) / ( np.log(z/z0) * np.log(z/z0q) )    # Dalton-Number
        
            # Bulk Richardson number
            Ri = 0
            if (u2!=0):
                Ri = ( (9.81 * (T2 - T0) * z) / (T2 * np.power(u2, 2)) ).item() #numba can't compare literal & array below

            # Stability correction
            phi = 1
            if (Ri > 0.01) & (Ri <= 0.2):
                phi = np.power(1-5*Ri,2)
            elif Ri > 0.2:
                phi = 0

            # Sensible heat flux
            H = rho * spec_heat_air * Cs_t * u2 * (T2-T0) * phi * np.cos(np.radians(SLOPE))
        
            # Latent heat flux
            LE = rho * Lv * Cs_q * u2 * (q2-q0) * phi * np.cos(np.radians(SLOPE))

        else:
            raise ValueError("Stability correction",stability_correction,"is not supported")	#numba refuses to print str(list)
        
    # -------------------------------------------------------------------------------------------------------------------- #

    elif turbulent_fluxes_method == 'Essery04':

        # ============================== #
        # Essery & Etchevers 2004 Method
        # ============================== #

        # Dry air density
        rho = (p*100.0) / (287.058 * T2)

        # Tubulent exchange coefficient:
        C_hn = 0.16 * np.power((np.log(z/z0)),-2) 

        fz = 0.25 * np.power((z0/z),0.5)
        Ri = 0
        if (u2!=0):
            Ri = ((9.81 * z / np.power(u2,2)) * (((T2 - T0)/T2) + ((q2 - q0)/(q2 + (0.622 / (1 - 0.622)))))).item()

        phi = 1
        if Ri >= 0:
            phi = (np.power((1 + (10 * Ri)),-1)).item()
        elif Ri < 0:
            phi = (1 - ((10 * Ri) * np.power((1 + ((10 * C_hn) * (np.sqrt(-Ri) / fz))),-1))).item()

        C_te = C_hn * phi

        # Sensible heat flux
        H = rho * spec_heat_air * C_te * u2 * (T2-T0) * np.cos(np.radians(SLOPE))
        
        # Latent heat flux
        LE = rho * Lv * C_te * u2 * (q2 - q0) * np.cos(np.radians(SLOPE))

        L = None
        Cs_t = None
        Cs_q = None

    # ======================= #
    # Longwave Radiation Flux
    # ======================= #

    Lo = -surface_emission_coeff * sigma * np.power(T0, 4.0)

    # ======================================== #
    # Ground Heat / Subsurface Conduction Flux
    # ======================================== #

    # Get thermal conductivity
    lam = GRID.get_node_thermal_conductivity(0)

    # Calculate ground / subsurface conduction flux
    hminus = subsurface_interpolation_depth_1
    hplus = subsurface_interpolation_depth_2 - subsurface_interpolation_depth_1
    Tz1, Tz2 = B_Ts
    B = lam * ((hminus/(hplus+hminus)) * ((Tz2-Tz1)/hplus) + (hplus/(hplus+hminus)) * ((Tz1-T0)/hminus))

    #B = lam * (Tz2 - T0) / subsurface_interpolation_depth_2

    # ============== #
    # Rain Heat Flux
    # ============== #

    QRR = water_density * spec_heat_water * (RAIN/1000/dt) * (T2 - T0)

    return (Li.item(), Lo.item(), H.item(), LE.item(), B.item(), QRR.item(), rho, Lv, L, Cs_t, Cs_q, q0, q2)

# ==================================================================================================================== # 

# ============================================================= #
# Interpolate Temperatures for Subsurface Heat Flux Computation
# ============================================================= #

@njit
def interp_subT(GRID):
    ''' Interpolate subsurface temperature & conductivities to depths used for the subsurface / ground heat flux computation'''
    
    # Cumulative layer depths
    layer_heights_cum = np.cumsum(np.array(GRID.get_height()))

    # Find indexes of two depths for temperature interpolation
    idx1_depth_1 = np.abs(layer_heights_cum - subsurface_interpolation_depth_1).argmin()
    depth_1 = layer_heights_cum.flat[np.abs(layer_heights_cum - subsurface_interpolation_depth_1).argmin()]

    if depth_1 > subsurface_interpolation_depth_1:
        idx2_depth_1 = idx1_depth_1 - 1
    else:
        idx2_depth_1 = idx1_depth_1 + 1
    Tz1 = GRID.get_node_temperature(idx1_depth_1) + \
		((GRID.get_node_temperature(idx1_depth_1) - GRID.get_node_temperature(idx2_depth_1)) / \
            	(layer_heights_cum[idx1_depth_1] - layer_heights_cum[idx2_depth_1])) * \
		(subsurface_interpolation_depth_1 - layer_heights_cum[idx1_depth_1])

    idx1_depth_2 = np.abs(layer_heights_cum - subsurface_interpolation_depth_2).argmin()
    depth_2 = layer_heights_cum.flat[np.abs(layer_heights_cum - subsurface_interpolation_depth_2).argmin()]

    if depth_2 > subsurface_interpolation_depth_2:
        idx2_depth_2 = idx1_depth_2 - 1
    else:
        idx2_depth_2 = idx1_depth_2 + 1

    Tz2 = GRID.get_node_temperature(idx1_depth_2) + \
		((GRID.get_node_temperature(idx1_depth_2) - GRID.get_node_temperature(idx2_depth_2)) / \
        	(layer_heights_cum[idx1_depth_2] - layer_heights_cum[idx2_depth_2])) * \
		(subsurface_interpolation_depth_2 - layer_heights_cum[idx1_depth_2])

    return np.array([Tz1,Tz2])
    
# ==================================================================================================================== #

# =============== #
# Extra Functions
# =============== #

@njit
def phi_m(z,L):
    """ Stability function for the momentum flux.
    """
    if (L>0):
        if ((z/L)>0.0) & ((z/L)<=1.0):
            return (-5*z/L)
        elif ((z/L)>1.0):
            return (1-5) * (1+np.log(z/L)) - (z/L) 
    elif L<0:
        x = np.power((1-16*z/L),0.25)
        return 2*np.log((1+x)/2.0) + np.log((1+np.power(x,2.0))/2.0) - 2*np.arctan(x) + np.pi/2.0
    else:
        return 0.0


@njit
def phi_tq(z,L):
    """ Stability function for the heat and moisture flux.
    """
    if (L>0):
        if ((z/L)>0.0) & ((z/L)<=1.0):
            return (-5*z/L)
        elif ((z/L)>1.0):
            return (1-5) * (1+np.log(z/L)) - (z/L) 
    elif L<0:
        x = np.power((1-19.3*z/L),0.25)
        return 2*np.log((1+np.power(x,2.0))/2.0)
    else:
        return 0.0


@njit
def ustar(u2,z,z0,L):
    """ Friction velocity. 
    """
    return (0.41*u2) / (np.log(z/z0)-phi_m(z,L))


@njit
def MO(rho, ust, T2, H):
    """ Monin-Obukhov length
    """
    # Monin-Obukhov length
    if H!=0:
        return ((rho*spec_heat_air*np.power(ust,3)*T2)/(0.41*9.81*H)).item()	#numba: expects a float
    else:
        return 0.0

@njit
def method_EW_Sonntag(T):
    ''' Saturation vapor pressure 
    
    Input:
        T   ::  Temperature [K]
    '''
    if T >= 273.16:
        # over water
        Ew = 6.112 * np.exp((17.67*(T-273.16)) / ((T-29.66)))
    else:
        # over ice
        Ew = 6.112 * np.exp((22.46*(T-273.16)) / ((T-0.55)))
    return Ew

# ==================================================================================================================== #