"""
    ==================================================================

              CREATE METEOROLOGICAL (METEO) INPUT FILE PROGRAM

        This file creates the model input meteo file that contains 
        contains the meteorological data varying through time (t)
        from an CSV file with the following variables:

        DATETIME (t)   ::    Datetime [yyyy-mm-dd hh:mm]
        T2 (t)         ::    Air temperature [K]
        U2 (t)         ::    Wind speed [m s-1]
        RH2 (t)        ::    Relative humidity [%]
        PRES (t)       ::    Atmospheric pressure [hPa]
        RRR (t)        ::    Precipitation [mm]
        N (t)          ::    Fractional cloud cover [0-1]

        Alternatively, instead of using fractional cloud cover (N),
        the user can specify directly measured radiative fluxes:

        SWin (t)       ::    Shortwave radiation [W m-2]
        LWin (t)       ::    Longwave radiation [W m-2]

        Optional Variables:

        T2_LAPSE (t)                 ::    Air Temperature Lapse Rate [K m-1]
        D (t)                        ::    Precipitation Downscaling Coefficient [-]
        PRECIPITATION_ANOMALY (t)    ::    Annual Precipitation Anomaly [-]
        

    ==================================================================
"""

import sys
import os
import xarray as xr
import pandas as pd
import numpy as np
import netCDF4 as nc
import time
import dateutil
import argparse
from itertools import product

# ============================================================================================= #

def create_meteo_input(csv_file, meteo_file, start_date = None, end_date = None):
    """ The create meteo program creates the input meteorological (meteo) file:

        Parameters:
                Start date       ::    Start date of meterological data subset [yyyy-mm-dd hh:mm]
                End date         ::    End date of meterological data subset [yyyy-mm-dd hh:mm]
        Input:
                Meteo CSV (t)    ::    CSV file containing meteorological data
        Output:
                METEO (t)        ::    Xarray dataset containing meteorological data

    """
      
    print('\n\t ==========================')
    print('\t CREATE METEOROLOGICAL FILE')
    print('\t ==========================\n')

    # ============================ #
    # Read CSV Meteorological Data
    # ============================ #

    # Load meteorological data:
    df = pd.read_csv(os.path.join('../../data/meteo/CSV/',csv_file), delimiter = ',')

    # Check input data:
    required_variables = {'DATETIME','T2', 'PRES', 'U2', 'RH2'}
    if not (required_variables.issubset(df.columns) and \
       ({'N'}.issubset(df.columns) or {'SWin', 'LWin'}.issubset(df.columns)) and \
       ({'RRR'}.issubset(df.columns) or {'D', 'ACC_ANOMALY'}.issubset(df.columns))):    
        print('\t Missing variables. The meteo dataset must have the following variables:\n\n', \
              '\t DATETIME - Datetime [yyyy-mm-dd hh:mm]\n', \
              '\t T2       - Air temperature [K]\n',  \
              '\t U2       - Wind speed [m s\u207b\xb9]\n', \
              '\t RH2      - Relative humidity [%]\n', \
              '\t PRES     - Atmospheric pressure [hPa]\n', \
              '\t RRR      - Precipitation [mm]\n', \
              '\t N        - Fractional cloud cover [0-1]\n\n', \
              '\t Alternatively, instead of using fractional cloud cover (N), the user can specify directly measured radiative fluxes:\n\n', \
              '\t SWin     - Shortwave radiation [W m\u207b\xb2]\n', \
              '\t LWin     - Longwave  radiation [W m\u207b\xb2]\n')
        raise ValueError('Error: Missing meteorological variables')

    # Check for NaNs:
    if df.isnull().values.any() == True:
        raise ValueError('Error: NaN Values are in the Dataset!')
    
    # Re-load meteorological data with dates parsing:
    df = pd.read_csv(os.path.join('../../data/meteo/CSV/',csv_file), delimiter = ',', index_col = ['DATETIME'], parse_dates = ['DATETIME'])

    # ===================== #
    # Select Temporal Range
    # ===================== #

    if ((start_date != None) & (end_date !=None)): 
        df = df.loc[start_date:end_date] 

    print('\t INFORMATION:')
    print('\t ==============================================================')
    print('\t Temporal range from %s until %s. Time steps: %s ' % (df.index[0],df.index[-1],len(df)))
    print('\t Input Meteorological Data CSV: ',csv_file)
    print('\t Output Meteorological Dataset: ',meteo_file,'\n')
    print('\t ==============================================================')

    # ======================= #
    # Create Xarray Dataframe 
    # ======================= #

    ds = xr.Dataset()
    ds.coords['time'] = df.index.values

    # ======================== #
    # Meteorological Variables
    # ======================== #

    print('\t METEOROLOGICAL VARIABLES:')
    print('\t ==============================================================')
    
    # Air Temperature [T2]
    print(f"\t 'T2' - Air Temperature at 2 m [K]                   Min: {np.round(df['T2'].min(),2)} -- Max: {np.round(df['T2'].max(),2)}")
    T2 = np.asarray(df['T2'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, T2, 'T2', 'K', 'Air Temperature at 2 m')

    # Air Temperature Lapse Rate [T2]
    if 'T2_LAPSE' in df.columns:
        print(f"\t 'T2_LAPSE' - Air Temperature Lapse Rate [K m\u207b\xb9]     Min: {np.round(df['T2_LAPSE'].min(),2)} -- Max: {np.round(df['T2_LAPSE'].max(),2)}")
        T2_LAPSE = np.asarray(df['T2_LAPSE'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, T2_LAPSE, 'T2_LAPSE', 'K m\u207b\xb9', 'Air Temperature Lapse Rate')

    # Atmospheric Pressure [PRES]
    print(f"\t 'PRES' - Atmospheric Pressure at 2 m [hPa]          Min: {np.round(df['PRES'].min(),2)} -- Max: {np.round(df['PRES'].max(),2)}")
    PRES = np.asarray(df['PRES'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, PRES, 'PRES', 'hPa', 'Atmospheric Pressure at 2 m')

    # Wind Speed [U2]
    print(f"\t 'U2' - Wind Speed at 2 m [m s\u207b\xb9]                    Min: {np.round(df['U2'].min(),2)} -- Max: {np.round(df['U2'].max(),2)}")
    U2 = np.asarray(df['U2'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, U2, 'U2', 'm s\u207b\xb9', 'Wind Speed at 2 m')

    # Relative Humidity [RH2]
    print(f"\t 'RH2' - Relative Humidity at 2 m [%]                Min: {np.round(df['RH2'].min(),2)} -- Max: {np.round(df['RH2'].max(),2)}")
    RH2 = np.asarray(df['RH2'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, RH2, 'RH2', '%', 'Relative Humidity at 2 m')

    # Shortwave Radiation [SWin]
    if 'SWin' in df.columns:
        print(f"\t 'SWin' - Incoming Shortwave Radiation [W m\u207b\xb2]       Min: {np.round(df['SWin'].min(),2)} -- Max: {np.round(df['SWin'].max(),2)}")
        SWin = np.asarray(df['SWin'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, SWin, 'SWin', 'W m\u207b\xb2', 'Incoming Shortwave Radiation')

    # Longwave Radiation [LWin]
    if 'LWin' in df.columns:
        print(f"\t 'LWin' - Incoming Longwave Radiation [W m\u207b\xb2]        Min: {np.round(df['LWin'].min(),2)} -- Max: {np.round(df['LWin'].max(),2)}")
        LWin = np.asarray(df['LWin'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, LWin, 'LWin', 'W m\u207b\xb2', 'Incoming Longwave Radiation')

    # Fractional Cloud Cover [N]
    if 'N' in df.columns:
        print(f"\t 'N' - Fractional Cloud Cover [-]                    Min: {np.round(df['N'].min(),2)} -- Max: {np.round(df['N'].max(),2)}")
        N = np.asarray(df['N'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, N, 'N', '-', 'Fractional Cloud Cover')

    # Precipitation [mm]
    if 'RRR' in df.columns:
        print(f"\t 'RRR' - Precipitation (solid/liquid) [mm]           Min: {np.round(df['RRR'].min(),2)} -- Max: {np.round(df['RRR'].max(),2)}")
        RRR = np.asarray(df['RRR'].apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
        add_variable_along_time(ds, RRR, 'RRR', 'mm', 'Precipitation (solid/liquid)')
    
    # Precipitation Downscaling Coefficient [-]
    if 'D' in df.columns:
        print(f"\t 'D' - Precipitation Downscaling Coefficient [-]     Min: {np.round(df['D'].min(),5)} -- Max: {np.round(df['D'].max(),5)}")
        D = np.asarray(df['D'].apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
        add_variable_along_time(ds, D, 'D', '-', 'Precipitation Downscaling Coefficient')

    # Annual Precipitation Anomaly [-]
    if 'PRECIPITATION_ANOMALY' in df.columns:
        print(f"\t 'PRECIPITATION_ANOMALY' - Annual Precipitation Anomaly [-]     Min: {np.round(df['PRECIPITATION_ANOMALY'].min(),2)} -- Max: {np.round(df['PRECIPITATION_ANOMALY'].max(),2)}")
        PRECIPITATION_ANOMALY = np.asarray(df['PRECIPITATION_ANOMALY'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, PRECIPITATION_ANOMALY, 'PRECIPITATION_ANOMALY', '-', 'Annual Precipitation Anomaly')

    print('\t ==============================================================')

    # ============================== #
    # Write Input Meteo File to Disc 
    # ============================== #

    ds.to_netcdf(os.path.join('../../data/meteo/',meteo_file))

    print('\n\t =================================')
    print('\t INPUT METEOROLOGICAL FILE CREATED')
    print('\t =================================\n')

# ============================================================================================= #

def add_variable_along_time(ds, var, name, units, long_name):
    """ This function adds variables to the METEO Xarray dataset (t) """
    	
    ds[name] = (('time'), var)
    ds[name].attrs['units'] = units
    ds[name].attrs['long_name'] = long_name
    return ds

# ============================================================================================= #

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create meteo input file from csv file.')
    parser.add_argument('-c', '-csv_file', dest='csv_file', help='Csv file(see readme for file convention)')
    parser.add_argument('-m', '-meteo_file', dest='meteo_file', help='Meteo file')
    parser.add_argument('-s', '-start_date', dest='start_date', help='Start date')
    parser.add_argument('-e', '-end_date', dest='end_date', help='End date')

    args = parser.parse_args()

    create_meteo_input(args.csv_file, args.meteo_file, args.start_date, args.end_date) 

# ============================================================================================= #
