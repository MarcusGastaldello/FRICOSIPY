"""
This program creates a 1-dimensional meteorological data input file from a csv
"""

# ================================ #
# Import Python modules & packages
# ================================ #

import sys
import xarray as xr
import pandas as pd
import numpy as np
import netCDF4 as nc
import time
import dateutil
import argparse
from itertools import product

sys.path.append('/home/gastalm/Data/meteo')

def create_meteo_input(csv_file, meteo_file, start_date = None, end_date = None):

    print('\n\t ==========================')
    print('\t CREATE METEOROLOGICAL FILE')
    print('\t ==========================\n')

    # ============================ #
    # Read CSV Meteorological Data
    # ============================ #

    print('\t (Note: Timestamps should be of the format: yyyy-mm-dd hh:mm:ss) \n')

    df = pd.read_csv(csv_file, delimiter = ',', index_col = ['TIMESTAMP'], parse_dates = ['TIMESTAMP'])

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

    if df.isnull().values.any() == True:
        print('\t Warning: NaN Values are in the Dataset! Abort')
        sys.exit()

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
        print(f"\t 'T2_LAPSE' - Air Temperature Lapse Rate [K m-1]     Min: {np.round(df['T2_LAPSE'].min(),2)} -- Max: {np.round(df['T2_LAPSE'].max(),2)}")
        T2_LAPSE = np.asarray(df['T2_LAPSE'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, T2_LAPSE, 'T2_LAPSE', 'K m-1', 'Air Temperature Lapse Rate')

    # Atmospheric Pressure [PRES]
    print(f"\t 'PRES' - Atmospheric Pressure at 2 m [hPa]          Min: {np.round(df['PRES'].min(),2)} -- Max: {np.round(df['PRES'].max(),2)}")
    PRES = np.asarray(df['PRES'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, PRES, 'PRES', 'hPa', 'Atmospheric Pressure at 2 m')

    # Wind Speed [U2]
    print(f"\t 'U2' - Wind Speed at 2 m [m s-1]                    Min: {np.round(df['U2'].min(),2)} -- Max: {np.round(df['U2'].max(),2)}")
    U2 = np.asarray(df['U2'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, U2, 'U2', 'm s-1', 'Wind Speed at 2 m')

    # Relative Humidity [RH2]
    print(f"\t 'RH2' - Relative Humidity at 2 m [%]                Min: {np.round(df['RH2'].min(),2)} -- Max: {np.round(df['RH2'].max(),2)}")
    RH2 = np.asarray(df['RH2'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
    add_variable_along_time(ds, RH2, 'RH2', '%', 'Relative Humidity at 2 m')

    # Shortwave Radiation [SWin]
    if 'SWin' in df.columns:
        print(f"\t 'SWin' - Incoming Shortwave Radiation [W m-2]       Min: {np.round(df['SWin'].min(),2)} -- Max: {np.round(df['SWin'].max(),2)}")
        SWin = np.asarray(df['SWin'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, SWin, 'SWin', 'W m-2', 'Incoming Shortwave Radiation')

    # Longwave Radiation [LWin]
    if 'LWin' in df.columns:
        print(f"\t 'LWin' - Incoming Longwave Radiation [W m-2]        Min: {np.round(df['LWin'].min(),2)} -- Max: {np.round(df['LWin'].max(),2)}")
        LWin = np.asarray(df['LWin'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, LWin, 'LWin', 'W m-2', 'Incoming Longwave Radiation')

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

    # Annual Accumulation Anomaly [-]
    if 'ACC_ANOMALY' in df.columns:
        print(f"\t 'ACC_ANOMALY' - Annual Accumulation Anomaly [-]     Min: {np.round(df['ACC_ANOMALY'].min(),2)} -- Max: {np.round(df['ACC_ANOMALY'].max(),2)}")
        ACC_ANOMALY = np.asarray(df['ACC_ANOMALY'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, ACC_ANOMALY, 'ACC_ANOMALY', '-', 'Annual Accumulation Anomaly')
    
    # Annual Sublimation Anomaly [-]
    if 'SUB_ANOMALY' in df.columns:
        print(f"\t 'SUB_ANOMALY' - Annual Sublimation Anomaly [-]      Min: {np.round(df['SUB_ANOMALY'].min(),2)} -- Max: {np.round(df['SUB_ANOMALY'].max(),2)}")
        SUB_ANOMALY = np.asarray(df['SUB_ANOMALY'].apply(pd.to_numeric, errors='coerce'), dtype = np.float32)
        add_variable_along_time(ds, SUB_ANOMALY, 'SUB_ANOMALY', '-', 'Annual Sublimation Anomaly')


    # ============================== #
    # Write Input Meteo File to Disc 
    # ============================== #

    ds.to_netcdf(meteo_file)

    print('\n\t =================================')
    print('\t INPUT METEOROLOGICAL FILE CREATED')
    print('\t =================================\n')

    # ============================================================================================= #

def add_variable_along_time(ds, var, name, units, long_name):
    """ This function adds variables to the METEO dataset """
    	
    ds[name] = (('time'), var)
    ds[name].attrs['units'] = units
    ds[name].attrs['long_name'] = long_name
    return ds

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create meteo input file from csv file.')
    parser.add_argument('-c', '-csv_file', dest='csv_file', help='Csv file(see readme for file convention)')
    parser.add_argument('-o', '-meteo_file', dest='meteo_file', help='Meteo file')
    parser.add_argument('-b', '-start_date', dest='start_date', help='Start date')
    parser.add_argument('-e', '-end_date', dest='end_date', help='End date')

    args = parser.parse_args()

    create_meteo_input(args.csv_file, args.meteo_file, args.start_date, args.end_date) 
