#!/usr/bin/env python

"""
    ======================================================================================================================================================

                                                                    FRICOSIPY VERSION 1.3.0

    This is the main executable file of the 'FRIbourg COupled Snowpack and Ice surface energy and mass balance glacier model in PYthon' (FRICOSIPY). 
    The original COSIPY model was initially written by Tobias Sauter and Anselm Ardnt (https://doi.org/10.5194/gmd-13-5645-2020) and developed by 
    Marcus Gastaldello into FRICOSIPY at the University of Fribourg (https://doi.org/10.5194/tc-19-2983-2025) for research at Colle Gnifetti, Monte Rosa.

    The latest version of the FRICOSIPY model can be obtained from : https://github.com/MarcusGastaldello/FRICOSIPY 

    Gastaldello, M. (2026). FRICOSIPY - University of Fribourg variant of the Coupled Snow and Ice model in Python (Version 1.3.0) [Computer software]. 
    https://github.com/MarcusGastaldello/FRICOSIPY

    ======================================================================================================================================================
"""

# Import Modules:
import os
from datetime import datetime
from itertools import product
import sys
from config import *
import dask.config
from main.kernel.fricosipy_core import * 
from main.kernel.io import *
from dask.distributed import Client, LocalCluster, as_completed
from tornado import gen
import logging

# Suppress excessive notifications from Distributed module (turn-off if debugging)
logging.getLogger("distributed").setLevel(logging.CRITICAL)

# =============================================================================================================== #

def main():

    print('\n\t =========================')
    print('\t FRICOSIPY MAIN SIMULATION')
    print('\t =========================\n')

    # Measure time
    simulation_start_time = datetime.now()

    # =============================== #
    # Create Input and Output Dataset
    # =============================== # 
    
    IO = IOClass()

    # Print information about the input datasets:
    print('\t INPUT DATASET INFORMATION:')
    print('\t ==============================================================')
    print('\t Input Static Dataset: ',static_netcdf)
    print('\t Input Meteorological Dataset: ',meteo_netcdf)
    print('\t Input Illumination Dataset: ',illumination_netcdf)
    print('\t --------------------------------------------------------------')

    # Load Input NetCDF Datasets:
    METEO = IO.load_meteo_file()
    STATIC = IO.load_static_file()
    ILLUMINATION = IO.load_illumination_file()

    # Create Output/Result NetCDF Dataset:
    RESULT = IO.create_result_file()

    # Output timesteps:
    timesteps = str(RESULT.sizes['time'])
    
    # Print information about the output dataset:
    print('\t OUTPUT DATASET INFORMATION:')
    print('\t ==============================================================')
    print('\t Output Dataset: ',output_netcdf)
    if reduced_output == True:
        print('\t Output Timestamps: ',output_timestamps)
    print('\t Output Timesteps: %s '% (timesteps))  
    print('\t --------------------------------------------------------------')
    print('\t Meteorological Variables (',len(IO.meteorological_variables),'):',IO.meteorological_variables)
    print('\t Surface Energy Fluxes    (',len(IO.surface_energy_fluxes),'):',IO.surface_energy_fluxes)
    print('\t Surface Mass Fluxes      (',len(IO.surface_mass_fluxes),'):',IO.surface_mass_fluxes)
    print('\t Subsurface Mass Fluxes   (',len(IO.subsurface_mass_fluxes),'):',IO.subsurface_mass_fluxes)
    print('\t Other Variables          (',len(IO.other),'):',IO.other)
        
    if full_field == True:
        print('\t Subsurface Variables     (',len(IO.subsurface_variables),'):',IO.subsurface_variables)
    else:
        print('\t Subsurface Variables : (Disabled)')
    print('\t ==============================================================\n')

    # ============================================ #
    # Create a Client for Distributed Calculations
    # ============================================ #

    with LocalCluster(scheduler_port = local_port, n_workers = workers, threads_per_worker = 1, silence_logs = True, processes = True) as cluster:
        run_fricosipy(cluster, IO, STATIC, METEO, ILLUMINATION, simulation_start_time)

    # ================== #
    # Write Result File:
    # ================== #
   
    encoding = dict()
    for var in IO.get_result().data_vars:
        encoding[var] = dict(zlib=True, complevel=compression_level)
  
    IO.get_result().to_netcdf(os.path.join(data_path,'output',output_netcdf), encoding=encoding, mode = 'w')
    
    simulation_time = int((datetime.now() - simulation_start_time).total_seconds())
    
    print(f"\n\t Total Simulation Duration: {int(simulation_time // 3600):02}:{int((simulation_time % 3600) // 60):02}:{int(simulation_time % 60):02}\n\n")
    print('\t =============================')
    print('\t FRICOSIPY Simulation Complete')
    print('\t =============================')

# =============================================================================================================== #

def run_fricosipy(cluster, IO, STATIC, METEO, ILLUMINATION, simulation_start_time):
    """ This function runs the FRICOSIPY simulation on a distributed computing cluster """

    with Client(cluster) as client:

        # Create Global Numpy Arrays which Aggregates all Local Results
        IO.create_global_result_arrays()

        # Generate a list of the spatial indexes of all glacial nodes: 
        nodes = [(y, x) for y, x in product(range(STATIC.sizes['y']), range(STATIC.sizes['x'])) if STATIC.MASK.isel(y=y, x=x).item() == 1]

        # Group nodes according to the number of workers available (i.e. the number that can run simulatenously)
        batches = [nodes[i:i + workers] for i in range(0, len(nodes), workers)]

        # Print paralleslisation information:
        info = client.scheduler_info()
        memory_limit = info['workers'][list(info['workers'].keys())[0]]['memory_limit'] / 1e9

        print('\t PARALLELISATION:')
        print('\t ==============================================================')
        print('\t',cluster)
        print('\t',client)
        print('\t --------------------------------------------------------------')
        print(f'\t Total memory: {(workers * memory_limit):.2f} GB RAM')
        print(f'\t Workers: {workers} ({memory_limit:.2f} GB RAM available per worker)')
        print('\t ==============================================================\n\n')

        print('\t ============================================================')
        print('\t Running FRICOSIPY simulation on',workers,'workers in',len(batches),'batches...')
        print('\t ============================================================\n')
        sys.stdout.flush()

        # Scatter shared meteorological input for faster computation:
        METEO_future = client.scatter(METEO, broadcast=True)

        # Simulate each batch sequentially
        completed_nodes = 0
        for i in range(len(batches)):

            # Start node simulation timer
            node_start_time = datetime.now()

            # Submit the spatial nodes to each worker and run the FRICOSIPY model
            futures = []
            for y,x in batches[i]:
                futures.append(client.submit(fricosipy_core, STATIC.isel(y=y, x=x), METEO_future, ILLUMINATION.isel(y=y, x=x), y, x, IO.nt, pure = False))
            
            # --- Main FRICOSIPY Simulation ---
            
            # Write the results collected from each worker to release memory
            for future in futures:

                # Get the results from the workers
                indY,indX, \
                AIR_TEMPERATURE,AIR_PRESSURE,RELATIVE_HUMIDITY,WIND_SPEED,FRACTIONAL_CLOUD_COVER, \
                SHORTWAVE,LONGWAVE,SENSIBLE,LATENT,GROUND,RAIN_FLUX,MELT_ENERGY, \
                RAIN,SNOWFALL,EVAPORATION,SUBLIMATION,CONDENSATION,DEPOSITION,SURFACE_MELT,SURFACE_MASS_BALANCE, \
                REFREEZE,SUBSURFACE_MELT,RUNOFF,MASS_BALANCE, \
                SNOW_HEIGHT,SNOW_WATER_EQUIVALENT,TOTAL_HEIGHT,SURFACE_TEMPERATURE,SURFACE_ALBEDO,N_LAYERS,FIRN_TEMPERATURE,FIRN_TEMPERATURE_CHANGE,FIRN_FACIE, \
                LAYER_DEPTH,LAYER_HEIGHT,LAYER_DENSITY,LAYER_TEMPERATURE,LAYER_WATER_CONTENT,LAYER_COLD_CONTENT,LAYER_POROSITY,LAYER_ICE_FRACTION, \
                LAYER_IRREDUCIBLE_WATER,LAYER_REFREEZE,LAYER_HYDRO_YEAR,LAYER_GRAIN_SIZE = future.result()
                                
                IO.copy_local_to_global(indY,indX, \
                AIR_TEMPERATURE,AIR_PRESSURE,RELATIVE_HUMIDITY,WIND_SPEED,FRACTIONAL_CLOUD_COVER, \
                SHORTWAVE,LONGWAVE,SENSIBLE,LATENT,GROUND,RAIN_FLUX,MELT_ENERGY, \
                RAIN,SNOWFALL,EVAPORATION,SUBLIMATION,CONDENSATION,DEPOSITION,SURFACE_MELT,SURFACE_MASS_BALANCE, \
                REFREEZE,SUBSURFACE_MELT,RUNOFF,MASS_BALANCE, \
                SNOW_HEIGHT,SNOW_WATER_EQUIVALENT,TOTAL_HEIGHT,SURFACE_TEMPERATURE,SURFACE_ALBEDO,N_LAYERS,FIRN_TEMPERATURE,FIRN_TEMPERATURE_CHANGE,FIRN_FACIE, \
                LAYER_DEPTH,LAYER_HEIGHT,LAYER_DENSITY,LAYER_TEMPERATURE,LAYER_WATER_CONTENT,LAYER_COLD_CONTENT,LAYER_POROSITY,LAYER_ICE_FRACTION, \
                LAYER_IRREDUCIBLE_WATER,LAYER_REFREEZE,LAYER_HYDRO_YEAR,LAYER_GRAIN_SIZE)

                # Update progress bar:
                completed_nodes += 1
                report_progress(completed_nodes,len(nodes),simulation_start_time,node_start_time)

            # Write results to file
            IO.write_results_to_file()

# =============================================================================================================== #

def report_progress(completed,total_nodes,simulation_start_time,node_start_time):
    barLength = 50 # Modify this to change the length of the progress bar
    progress = completed / total_nodes
    node_time = int((datetime.now() - node_start_time).total_seconds())
    total_time = int((datetime.now() - simulation_start_time).total_seconds())
    block = int(round(barLength*progress))
    update = (
    f"\t [{'#' * block + '-' * (barLength - block)}] | {completed} / {total_nodes} Nodes simulated | "
    f"{round(progress * 100, 2)}% | "
    f"Node time: {int(node_time // 3600):02}:{int((node_time % 3600) // 60):02}:{int(node_time % 60):02} | "
    f"Total time: {int(total_time // 3600):02}:{int((total_time % 3600) // 60):02}:{int(total_time % 60):02}\n")
    sys.stdout.write(update)
    sys.stdout.flush()

''' MODEL EXECUTION '''
if __name__ == "__main__":
    main()

# =============================================================================================================== #
