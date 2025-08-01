"""
This program creates a 3-dimensional illumination data input file for a normal and leap year from a static file
"""
import sys
import xarray as xr
import pandas as pd
import numpy as np
import netCDF4 as nc
import time
import math as mt
import dateutil
from itertools import product
import argparse
from numba import njit

sys.path.append('/home/gastalm/Data/illumination')

def create_illumindation_file(static_file, illumination_file):

      print('\n\t ========================')
      print('\t CREATE ILLUMINATION FILE')
      print('\t ========================\n')

      print('\t Note: Glacier nodes cannot exist on the boundary of the static spatial domain!\n')

      # ================ #
      # Load static data
      # ================ #

      ds = xr.open_dataset(static_file)   

      print('\t INFORMATION:')
      print('\t ==============================================================')
      print('\t Input Static Dataset: ',static_file)
      print('\t Output Illumination Dataset: ',illumination_file,'\n')

      # ========================== #
      # Create Auxillary Variables 
      # ========================== # 

      # Auxiliary variables
      Elevation = ds.ELEVATION.values
      Mask = ds.MASK.values
      Latitude = ds.LATITUDE.values
      Longitude = ds.LONGITUDE.values
      Northing = ds.NORTHING.values
      Easting = ds.EASTING.values

      # ===================================== #
      # Create Numpy Arrays for the 2D Fields
      # ===================================== #

      Illumination_Norm = np.zeros([8784, len(ds.y), len(ds.x)], dtype = np.int8)
      Illumination_Leap = np.zeros([8784, len(ds.y), len(ds.x)], dtype = np.int8)

      # ===================================================== #
      # Calulcate the Topographic Shading Illumination Matrix
      # ===================================================== #

      print('\t Calculating Topographic Shading Illumination Matrix for a Normal Year:\n')
      sys.stdout.flush() 
      time_rad = np.linspace(0,2 *np.pi,8760)
      hour = np.tile(np.linspace(0,23,24),365)
      for t in range(8784):
        if t < 8760:
            Illumination_Norm[t,:,:] = Topographic_Shading(Latitude,Longitude,Northing,Easting,Elevation,Mask,time_rad[t],hour[t],Illumination_Norm[t,:,:])
        else:
            Illumination_Norm[t,:,:] = 0

            
      print('\t Calculating Topographic Shading Illumination Matrix for a Leap Year:\n') 
      sys.stdout.flush()
      time_rad = np.linspace(0,2 *np.pi,8784)
      hour = np.tile(np.linspace(0,23,24),366)   
      for t in range(8784):
            Illumination_Leap[t,:,:] = Topographic_Shading(Latitude,Longitude,Northing,Easting,Elevation,Mask,time_rad[t],hour[t],Illumination_Leap[t,:,:])


      # Save the Calculated Illumination Matrix:
      f = nc.Dataset(illumination_file, 'w')
      f.createDimension('hour', 8784)
      f.createDimension('y', len(ds.y))
      f.createDimension('x', len(ds.x))
      northing_values = ds.y.values
      easting_values = ds.x.values

      NORTHINGS = f.createVariable('y', 'f4', ('y',))
      NORTHINGS.units = 'm'
      NORTHINGS.long_name = 'projection_y_coordinate'
      NORTHINGS.standard_name = 'projection_y_coordinate'
      NORTHINGS.axis = 'Y'
      NORTHINGS[:] = northing_values
        
      EASTINGS = f.createVariable('x', 'f4', ('x',))
      EASTINGS.units = 'm'
      EASTINGS.long_name = 'projection_x_coordinate'
      EASTINGS.standard_name = 'projection_x_coordinate'
      EASTINGS.axis = 'X'
      EASTINGS[:]  = easting_values

      ILLUMINATON_NORM = f.createVariable('ILLUMINATION_NORM', np.int32, ('hour', 'y', 'x'))
      ILLUMINATON_NORM.long_name = 'Topographic Shading Illumination (Normal Year)'
      ILLUMINATON_NORM[:] = Illumination_Norm

      ILLUMINATON_LEAP = f.createVariable('ILLUMINATION_LEAP', np.int32, ('hour', 'y', 'x'))
      ILLUMINATON_LEAP.long_name = 'Topographic Shading Illumination (Leap Year)'
      ILLUMINATON_LEAP[:] = Illumination_Leap

      print('\n\t =========================')
      print('\t Illumination File Created')
      print('\t =========================\n')
            
      f.close()

def Topographic_Shading(latitude,longitude,northing,easting,height,mask,time_rad,hour,Illumination):

      # =============================== #
      # Solar Declination: (in radians)   
      # =============================== #

      Declination = 0.322003 - 22.971 * np.cos(time_rad) - 0.357898 * np.cos(2 * time_rad) - 0.14398 * np.cos(3 * time_rad) + 3.94638 * np.sin(time_rad) + 0.019334 * np.sin(2 * time_rad) + 0.05928 * np.sin(3 *time_rad)

      # ============================== #
      # Solar Hour Angle: (in degrees)
      # ============================== #

      Equation_of_time = 229.18 * (0.000075 + 0.001868 * np.cos(time_rad) - 0.032077 * np.sin(time_rad) - 0.014615 * np.cos(2 * time_rad) - 0.040849 * np.sin(2 * time_rad))
      Time_offset = Equation_of_time + (4 * longitude)           # in minutes
      Local_solar_time = hour + (Time_offset / 60)               # in decimal hours
      Solar_hour_angle = -(15 * (Local_solar_time - 12))         # in degrees (180 at midnight, 90 at sunrise, 0 at midday, 270 at sunset)

      # ====================================== #
      # Solar Elevation / Zenith: (in radians)
      # ====================================== #

      Solar_Elevation = np.arcsin(np.sin(np.radians(Declination)) * np.sin(np.radians(latitude)) + np.cos(np.radians(Declination)) * np.cos(np.radians(latitude)) * np.cos(np.radians(Solar_hour_angle)))
      
      # Only perform calculations when the sun is over the horizon:
      if np.nanmax(Solar_Elevation) > 0: 
            
            # ================================= #
            # Solar Azimuth Angle: (in radians)
            # ================================= #

            Azimuth = np.arccos((np.sin(np.radians(Declination)) * np.cos(np.radians(latitude)) - np.cos(np.radians(Declination)) * np.sin(np.radians(latitude)) * np.cos(np.radians(Solar_hour_angle))) / np.cos(Solar_Elevation))
            Azimuth = np.where(Solar_hour_angle < 0, Azimuth * -1, Azimuth)

            # ==================== #
            # Topographic Shading:
            # ==================== #

            # Define altitude matrix:
            z = height

            # Acquire grid dimensions:
            len_y, len_x = height.shape

            # Define maximum radius (of DEM area) in metres
            rmax = ((np.linalg.norm(np.max(northing) - np.min(northing))) ** 2 + (np.linalg.norm(np.max(easting) - np.min(easting))) ** 2) ** 0.5
            nums = int(rmax * len(northing) / (np.max(northing) - np.min(northing)))

            # Calculate direction to sun
            beta = (mt.pi/2) - np.nanmean(Azimuth)
            dy = np.sin(beta) * rmax  # walk into sun direction (y) as far as rmax
            dx = np.cos(beta) * rmax  # walk into sun direction (x) as far as rmax

            # Extract profile to sun from each (glacier) grid point
            for y in range(len_y):
                  for x in range(len_x):
                        if mask[y,x] == 1:

                                    start = (northing[y,x], easting[y,x]) 
                                    targ = (start[0] + dy, start[1] + dx)  # find target position

                                    # Points along profile (northing/easting)
                                    northing_list = np.linspace(start[0], targ[0], nums)  # equally spread points along profile
                                    easting_list = np.linspace(start[1], targ[1], nums)  # equally spread points along profile

                                    # Don't walk outside DEM boundaries
                                    northing_list_reduced = northing_list[(northing_list < np.max(northing)) & (northing_list > np.min(northing))]
                                    easting_list_reduced  = easting_list[(easting_list < np.max(easting))    & (easting_list > np.min(easting))]

                                    # Cut to same extent
                                    if (len(northing_list_reduced) > len(easting_list_reduced)):
                                          northing_list_reduced = northing_list_reduced[0:len(easting_list_reduced)]
                                    if (len(easting_list_reduced) > len(northing_list_reduced)):
                                          easting_list_reduced = easting_list_reduced[0:len(northing_list_reduced)]

                                    # Find indices (instead of northing/easting) at closets gridpoint
                                    idy = (y, (np.abs(np.unique(northing)  - northing_list_reduced[-1])).argmin())
                                    idx = (x, (np.abs(np.unique(easting)   - easting_list_reduced[-1])).argmin())

                                    # Points along profile (indices)
                                    y_list = np.round(np.linspace(idy[0], idy[1], len(northing_list_reduced)))
                                    x_list = np.round(np.linspace(idx[0], idx[1], len(easting_list_reduced)))

                                    # Calculate altitude along profile
                                    z = height[y_list.astype(np.int32), x_list.astype(np.int32)]

                                    # Calclulate DISTANCE along profile
                                    distance = ((northing_list_reduced - start[0]) ** 2 + (easting_list_reduced - start[1]) ** 2) ** 0.5

                                    # Topography angle
                                    topography_angle = np.degrees(np.arctan((z[1:len(z)] - z[0]) / distance[1:len(distance)]))

                                    if np.max(topography_angle) > np.nanmean(np.degrees(Solar_Elevation)):
                                          Illumination[y,x] = 0
                                    else:
                                          Illumination[y,x] = 1

      mask[mask==0] = 0
      Illumination = Illumination * mask

      return Illumination

if __name__ == "__main__":
    
      parser = argparse.ArgumentParser(description='Create illumination file from csv file.')
      parser.add_argument('-s', '-static_file', dest='static_file', help='Static file containing DEM, Slope etc.')
      parser.add_argument('-i', '-illumination_file', dest='illumination_file', help='Illumination matrix containing topographic shading boolean')

      args = parser.parse_args()

      create_illumindation_file(args.static_file, args.illumination_file) 


