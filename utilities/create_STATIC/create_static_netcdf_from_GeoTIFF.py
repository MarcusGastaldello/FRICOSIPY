"""
    ==================================================================

                 CREATE STATIC INPUT FILE PROGRAM (from GeoTIFF)

        This file creates the model input static file that contains 
        topographic information that varies across the spatial 
        domain (x,y) from an GeoTIFF and Shapefile with the following
        variables:

        NORTHING (x,y)       ::    Northing [m]
        EASTING (x,y)        ::    Easting [m]
        LATITUDE (x,y)       ::    Latitude (WGS84) [decimal]
        LONGITUDE (x,y)      ::    Longitude (WGS84) [decimal]
        ELEVATION (x,y)      ::    Elevation [m a.s.l.]
        ASPECT (x,y)         ::    Terrain aspect [°]
        SLOPE (x,y)          ::    Terrain slope [°]
        MASK (x,y)           ::    Glacier mask boolean [0 or 1]

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
import rasterio
import fiona
from rasterio.warp import transform
from rasterio.features import geometry_mask
import rioxarray as rio
import warnings
warnings.filterwarnings("ignore", message = "angle from rectified to skew grid parameter lost")

# ============================================================================================= #

def create_static_input(geoTIFF_file, shapefile, static_file, resolution = None):
    """ The create static program creates the input static file:

        Input:
                GeoTIFF (x,y)        ::    Digital Elevation Model in GeoTIFF format containing topographic data
                Shapefile (x,y)      ::    Shapefile demarcating the glacier outline / mask
                Resolution           ::    Resampled resolution of the static dataset (optional)

        Output:
                STATIC (x,y)        ::    Xarray dataset containing topographic/static data

    """
    print('\n\t ==================')
    print('\t CREATE STATIC FILE')
    print('\t ==================\n')

    with rasterio.open(os.path.join('../../data/static/GeoTIFF/',geoTIFF_file)) as src:

        # ==================== #
        # Read CSV Static Data
        # ==================== #

                 
        # Print Information:
        print('\t INFORMATION:')
        print('\t ==============================================================')
        print('\t Input GeoTIFF Digital Elevation Model (DEM): ',geoTIFF_file)
        print('\t Input Glacier Mask Shapefile (SHP): ',shapefile)
        print('\t Output Static NetCDF Dataset: ',static_file)
        print('\t --------------------------------------------------------------')

        # ================== #
        # Spatial Resoultion
        # ================== #

        print('\t Digital Elevation Model (DEM) Spatial Resolution: ',src.res[0],' m')
        print('\t ==============================================================\n')

        # ======================== #
        # Extract Topographic Data
        # ======================== #

        # Easting [EASTING] and Northing [NORTHING]:
        cols, rows = np.meshgrid(np.arange(src.width), np.arange(src.height))
        eastings, northings = rasterio.transform.xy(src.transform, rows, cols)
        EASTING = np.array(eastings)
        NORTHING = np.array(northings)

        # Elevation [ELEVATION]:
        ELEVATION = src.read(1).astype('float64')
        ELEVATION[ELEVATION == src.nodata] = np.nan

        # Slope [SLOPE] & Aspect [ASPECT]:
        res_x, res_y = src.res
        dz_dx, dz_dy = np.gradient(ELEVATION, res_x, res_y)
        SLOPE = np.degrees(np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)))
        ASPECT = np.degrees(np.arctan2(-dz_dx, dz_dy)) % 360

        # Latitude [LATITUDE] & Longitude [LONGITUDE]:
        longitudes, latitudes = transform(src.crs, 'EPSG:4326', EASTING.flatten(), NORTHING.flatten())
        LONGITUDE = np.array(longitudes).reshape(src.height, src.width)
        LATITUDE = np.array(latitudes).reshape(src.height, src.width)

        # Glacier Mask [MASK]
        with fiona.open(os.path.join('../../data/static/SHP/',shapefile), "r") as shp:
            geoms = [feature["geometry"] for feature in shp]
            mask_bool = geometry_mask(geoms, out_shape = src.shape, transform = src.transform, invert = True)
            MASK = mask_bool.astype(np.float64)

        # ======================= #
        # Create Xarray Dataframe 
        # ======================= #

        # Create Xarray Dataframe:
        EASTING = np.array(eastings).reshape((src.height, src.width))
        NORTHING = np.array(northings).reshape((src.height, src.width))
        ds = xr.Dataset(coords={'x': EASTING[0, :], 'y': NORTHING[:, 0]})

        # ================ #
        # Static Variables
        # ================ #

        print('\t STATIC VARIABLES:')
        print('\t ==============================================================')
    
        # Print information about static variables to the terminal:
        print(f"\t 'ELEVATION' - Elevation [m a.s.l.]                  Min: {np.round(ELEVATION.min(),2)} -- Max: {np.round(ELEVATION.max(),2)}")
        print(f"\t 'ASPECT' - Aspect [degree]                          Min: {np.round(ASPECT.min(),2)} -- Max: {np.round(ASPECT.max(),2)}")
        print(f"\t 'SLOPE' - Slope [degree]                            Min: {np.round(SLOPE.min(),2)} -- Max: {np.round(SLOPE.max(),2)}")
        print(f"\t 'MASK' - Mask [-]                                   Min: {np.round(MASK.min(),2)} -- Max: {np.round(MASK.max(),2)}")
        print(f"\t 'LATITUDE' - Latitude [decimal degree]              Min: {np.round(LATITUDE.min(),2)} -- Max: {np.round(LATITUDE.max(),2)}")
        print(f"\t 'LONGITUDE' - Longitude [decimal degree]            Min: {np.round(LONGITUDE.min(),2)} -- Max: {np.round(LONGITUDE.max(),2)}")

        # Add static variables to the Xarray dataset:
        add_variable_along_easting_northing(ds, NORTHING, 'NORTHING', 'm', 'Y Co-ordinate of Projection')
        add_variable_along_easting_northing(ds, EASTING, 'EASTING', 'm', 'X Co-ordinate of Projection')
        add_variable_along_easting_northing(ds, ELEVATION, 'ELEVATION', 'm a.s.l.', 'Elevation')   
        add_variable_along_easting_northing(ds, ASPECT, 'ASPECT', 'degree', 'Aspect')
        add_variable_along_easting_northing(ds, SLOPE, 'SLOPE', 'degree', 'Slope')
        add_variable_along_easting_northing(ds, MASK, 'MASK', 'm a.s.l.', 'Mask') 
        add_variable_along_easting_northing(ds, LATITUDE, 'LATITUDE', 'degree', 'Latitude')
        add_variable_along_easting_northing(ds, LONGITUDE, 'LONGITUDE', 'degree', 'Longitude')

        print('\t ==============================================================\n')

        # ========== #
        # Resampling
        # ========== #

        if resolution is not None:

            print('\t RESAMPLING SPATIAL GRID:')
            print('\t ==============================================================')

            # 
            target_resolution = float(resolution)
            left, bottom, right, top = src.bounds
            nx = int(np.round((right - left) / target_resolution))
            ny = int(np.round((top - bottom) / target_resolution))

            print('\t Resampled Grid Spatial Resolution: ',resolution,' m \n')
            print('\t ==============================================================')

            #
            resampled_x = np.linspace(left + target_resolution / 2, right - target_resolution / 2, nx)
            resampled_y = np.linspace(top - target_resolution / 2, bottom + target_resolution / 2, ny)

            # Interpolate data in the Xarray dataset to the new spatial resolution:
            ds = ds.interp(x = resampled_x, y = resampled_y, method = "linear")
            
            # Round glacier mask values to the nearest interger (boolean):
            ds['MASK'] = np.round(ds['MASK'])

        # =============================== #
        # Write Input Static File to Disc 
        # =============================== #

        # Assign Co-ordinate Reference System (CRS):
        ds = ds.sortby(['x', 'y'])
        ds = ds.rio.set_spatial_dims(x_dim = "x", y_dim = "y", inplace = True)
        ds = ds.rio.write_crs(src.crs, inplace = True)
        ds = ds.rio.write_coordinate_system(inplace = True)

        # Write static NetCDF file:
        ds.to_netcdf(os.path.join('../../data/static/',static_file))

        print('\n\t =========================')
        print('\t INPUT STATIC FILE CREATED')
        print('\t =========================\n')

# ============================================================================================= #

def add_variable_along_easting_northing(ds, var, name, units, long_name):
    """ This function adds variables to the STATIC Xarray dataset (x,y) """
    	
    ds[name] = (('y','x'), var)
    ds[name].attrs['units'] = units
    ds[name].attrs['long_name'] = long_name
    ds[name].attrs['grid_mapping'] = 'spatial_ref'
    ds[name].encoding['_FillValue'] = -9999
    return ds

# ============================================================================================= #

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Create 2D input file from a GeoTIFF file.')
    parser.add_argument('-g', '-geotiff_file', dest='geotiff_file', help='GeoTIFF file containing a Digital Elevation Model (DEM)')
    parser.add_argument('-m', '-shapefile', dest='shapefile', help='Shapefile demarcating glacier outline')
    parser.add_argument('-s', '-static_file', dest='static_file', help='Static file containing DEM, Slope etc.')
    parser.add_argument('-r', '-resolution',  dest='resolution',  help='Spatial resolution of static file')

    args = parser.parse_args()

    create_static_input(args.geotiff_file, args.shapefile, args.static_file, args.resolution)

# ============================================================================================= #

