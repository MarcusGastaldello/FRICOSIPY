"""
    ==================================================================

                 CREATE STATIC INPUT FILE PROGRAM (from CSV)

        This file creates the model input static file that contains 
        topographic information that varies across the spatial 
        domain (x,y) from an CSV file with the following variables:

        NORTHING (x,y)       ::    Northing [m]
        EASTING (x,y)        ::    Easting [m]
        LATITUDE (x,y)       ::    Latitude (WGS84) [decimal]
        LONGITUDE (x,y)      ::    Longitude (WGS84) [decimal]
        ELEVATION (x,y)      ::    Elevation [m a.s.l.]
        ASPECT (x,y)         ::    Terrain aspect [°]
        SLOPE (x,y)          ::    Terrain slope [°]
        MASK (x,y)           ::    Glacier mask boolean [0 or 1]

        Optional Variables:

        ACCUMULATION (x,y)   ::    Annual accumulation climatology [m w.e. a-1]
        SUBLIMATION (x,y)    ::    Annual sublimation climatology [m w.e. a-1]
        BASAL (x,y)          ::    Basal heat flux [mW m-2]
        THICKNESS (x,y)      ::    Glacier depth / thickness [m]

    ==================================================================
"""

import netCDF4
import os
import numpy as np
import csv
import sys
import datetime as dt
import argparse
import pandas as pd
import xarray as xr

# ============================================================================================= #

def create_static_input(csv_file, static_file):
    """ The create static program creates the input static file:

        Input:
                Static CSV (x,y)    ::    CSV file containing topographic/static data
        Output:
                STATIC (x,y)        ::    Xarray dataset containing topographic/static data

    """
    print('\n\t ==================')
    print('\t CREATE STATIC FILE')
    print('\t ==================\n')

    # ==================== #
    # Read CSV Static Data
    # ==================== #

    # Check for NaNs:
    df = pd.read_csv(csv_file)
    if df.isnull().values.any() == True:
        raise ValueError('Error: NaN Values are in the Dataset!')
    
    # Check input data:
    required_variables = {'EASTING', 'NORTHING', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'ASPECT', 'SLOPE', 'MASK'}
    if not required_variables.issubset(df.columns):
        print('Missing variables: The static dataset must have the following variables:\n\n', \
              '\t NORTHING  - Northing [m]\n', \
              '\t EASTING   - Easting  [m]\n',  \
              '\t LATITUDE  - Latitude  (WGS84) [decimal]\n', \
              '\t LONGITUDE - Longitude (WGS84) [decimal]\n', \
              '\t ELEVATION - Elevation [m a.s.l.]\n', \
              '\t ASPECT    - Aspect [°]\n', \
              '\t SLOPE     - Slope  [°]\n', \
              '\t MASK      - Glacier mask boolean [boolean]\n')
        raise ValueError('Error: Missing static variables')
                         
    # Print Information:
    print('\t INFORMATION:')
    print('\t ==============================================================')
    print('\t Input Static Data CSV: ',csv_file)
    print('\t Output Static NetCDF Dataset: ',static_file)
    print('\t --------------------------------------------------------------')
    print('\t Minimum Easting:  ',np.min(df["EASTING"]))
    print('\t Maximum Easting:  ',np.max(df["EASTING"]))
    print('\t Minimum Northing: ',np.min(df["NORTHING"]))
    print('\t Maximum Northing: ',np.max(df["NORTHING"]))

    # ================== #
    # Spatial Resoultion
    # ================== #

    # Calculate grid spatial resolution:
    if (np.unique(np.diff(np.unique(df["EASTING"]))) == np.unique(np.diff(np.unique(df["NORTHING"])))) and \
    (np.unique(np.diff(np.unique(df["EASTING"]))).size == 1) and (np.unique(np.diff(np.unique(df["NORTHING"]))).size == 1):
        resolution = np.unique(np.diff(np.unique(df["EASTING"])))[0]
        print('\t Grid Spatial Resolution: ',resolution,' m \n')
    else:
        raise ValueError('Error: Non-square grid detected!')

    # ======================= #
    # Create Xarray Dataframe 
    # ======================= #

    ds = xr.Dataset()
    ds.coords['x'] = df["EASTING"].unique()
    ds.coords['y'] = df["NORTHING"].unique()

    # Northing [NORTHING]
    NORTHING = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "NORTHING").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, NORTHING, 'NORTHING', 'm', 'Y Co-ordinate of Projection')

    # Easting [EASTING]
    EASTING = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "EASTING").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, EASTING, 'EASTING', 'm', 'X Co-ordinate of Projection')

    # ================ #
    # Static Variables
    # ================ #

    print('\t STATIC VARIABLES:')
    print('\t ==============================================================')
    
    # Elevation [ELEVATION]
    print(f"\t 'ELEVATION' - Elevation [m a.s.l.]                  Min: {np.round(df['ELEVATION'].min(),2)} -- Max: {np.round(df['ELEVATION'].max(),2)}")
    ELEVATION = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "ELEVATION").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, ELEVATION, 'ELEVATION', 'm a.s.l.', 'Elevation')

    # Aspect [ASPECT]
    print(f"\t 'ASPECT' - Aspect [degree]                          Min: {np.round(df['ASPECT'].min(),2)} -- Max: {np.round(df['ASPECT'].max(),2)}")
    ASPECT = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "ASPECT").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, ASPECT, 'ASPECT', 'degree', 'Aspect')

    # Slope [SLOPE]
    print(f"\t 'SLOPE' - Slope [degree]                            Min: {np.round(df['SLOPE'].min(),2)} -- Max: {np.round(df['SLOPE'].max(),2)}")
    SLOPE = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "SLOPE").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, SLOPE, 'SLOPE', 'degree', 'Slope')

    # Mask [MASK]
    print(f"\t 'MASK' - Mask [-]                                   Min: {np.round(df['MASK'].min(),2)} -- Max: {np.round(df['MASK'].max(),2)}")
    MASK = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "MASK").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    MASK[MASK == 0] = -9999
    add_variable_along_easting_northing(ds, MASK, 'MASK', 'm a.s.l.', 'Mask') 

    # Latitude [LATITUDE]
    print(f"\t 'LATITUDE' - Latitude [decimal degree]              Min: {np.round(df['LATITUDE'].min(),2)} -- Max: {np.round(df['LATITUDE'].max(),2)}")
    LATITUDE = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "LATITUDE").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, LATITUDE, 'LATITUDE', 'degree', 'Latitude')

    # Longitude [LONGITUDE]
    print(f"\t 'LONGITUDE' - Longitude [decimal degree]            Min: {np.round(df['LONGITUDE'].min(),2)} -- Max: {np.round(df['LONGITUDE'].max(),2)}")
    LONGITUDE = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "LONGITUDE").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
    add_variable_along_easting_northing(ds, LONGITUDE, 'LONGITUDE', 'degree', 'Longitude')

    # Precipitation Climatology [PRECIPITATION]
    if 'PRECIPITATION_CLIMATOLOGY' in df.columns:
        print(f"\t 'PRECIPITATION_CLIMATOLOGY' - Precipitation Climatology [m a\u207b\xb9]   Min: {np.round(df['PRECIPITATION_CLIMATOLOGY'].min(),2)} -- Max: {np.round(df['PRECIPITATION_CLIMATOLOGY'].max(),2)}")
        PRECIPITATION_CLIMATOLOGY = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "PRECIPITATION_CLIMATOLOGY").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
        add_variable_along_easting_northing(ds, PRECIPITATION_CLIMATOLOGY, 'PRECIPITATION_CLIMATOLOGY', 'm a\u207b\xb9', 'Precipitation Climatology')

    # Basal Heat Flux [BASAL]
    if 'BASAL' in df.columns:
        print(f"\t 'BASAL' - Basal Heat Flux [mW m\u207b\xb2]                  Min: {np.round(df['BASAL'].min(),2)} -- Max: {np.round(df['BASAL'].max(),2)}")
        BASAL = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "BASAL").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
        add_variable_along_easting_northing(ds, BASAL, 'BASAL', 'mW m\u207b\xb2', 'Basal Heat Flux')
    
    # Glacier Thickness [THICKNESS]
    if 'THICKNESS' in df.columns:
        print(f"\t 'THICKNESS' - Glacier Thickness [m]                         Min: {np.round(df['THICKNESS'].min(),2)} -- Max: {np.round(df['THICKNESS'].max(),2)}")
        THICKNESS = np.asarray(df.pivot(index = "NORTHING", columns = "EASTING", values = "THICKNESS").apply(pd.to_numeric, errors='coerce'), dtype = np.float64)
        add_variable_along_easting_northing(ds, THICKNESS, 'THICKNESS', 'm', 'Glacier Thickness')

    # =============================== #
    # Write Input Static File to Disc 
    # =============================== #

    #ds.rio.write_crs("epsg:2056", inplace=True) # Incompatible with current Python 3.6
    ds.to_netcdf(static_file)

    print('\n\t =========================')
    print('\t INPUT STATIC FILE CREATED')
    print('\t =========================\n')

# ============================================================================================= #

def add_variable_along_easting_northing(ds, var, name, units, long_name):
    """ This function adds variables to the STATIC Xarray dataset (x,y) """
    	
    ds[name] = (('y','x'), var)
    ds[name].attrs['units'] = units
    ds[name].attrs['long_name'] = long_name
    ds[name].encoding['_FillValue'] = -9999
    return ds

# ============================================================================================= #

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create 2D input file from csv file.')
    parser.add_argument('-c', '-csv_file', dest='csv_file', help='Csv file(see readme for file convention)')
    parser.add_argument('-s', '-static_file', dest='static_file', help='Static file containing DEM, Slope etc.')

    args = parser.parse_args()

    create_static_input(args.csv_file, args.static_file)


# ============================================================================================= #
