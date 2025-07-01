#!/usr/bin/env python

"""
    This is the main code file of the 'FRIbourg COupled Snowpack and Ice surface energy
    and mass balance glacier model in PYthon' (FRICOSIPY). The original COSIPY model was initially written by
    Tobias Sauter and Anselm Ardnt (https://doi.org/10.5194/gmd-13-5645-2020) and developed by 
    Marcus Gastaldello into FRICOSIPY for detailed firn modelling at the University of Fribourg.
"""

# Import Modules:
import os
from datetime import datetime
from itertools import product
import sys
from config import *
from main.kernel.fricosipy_core import * 
from main.kernel.io import *
from dask.distributed import Client, LocalCluster, as_completed
from tornado import gen

def main():

    print('\n\t =========================')
    print('\t FRICOSIPY MAIN SIMULATION')
    print('\t =========================\n')

    # =============================== #
    # Create input and output dataset
    # =============================== # 
    IO = IOClass()
    METEO = IO.load_meteo_file()
    STATIC = IO.load_static_file()
    ILLUMINATION = IO.load_illumination_file()
    
    # Create Global Result Dataset
    RESULT = IO.create_result_file()

    print('\t OUTPUT VARIABLES:')
    print('\t ==============================================================')
    print('\t Meteorological Variables (',len(IO.meteorological_variables),'):',IO.meteorological_variables)
    print('\t Surface Energy Fluxes (',len(IO.surface_energy_fluxes),'):',IO.surface_energy_fluxes)
    print('\t Surface Mass Fluxes (',len(IO.surface_mass_fluxes),'):',IO.surface_mass_fluxes)
    print('\t Subsurface Mass Fluxes (',len(IO.subsurface_mass_fluxes),'):',IO.subsurface_mass_fluxes)
    print('\t Other Variables (',len(IO.other),'):',IO.other)
    if full_field == True:
        print('\t Subsurface Variables (',len(IO.subsurface_variables),'):',IO.subsurface_variables)
    else:
        print('\t Subsurface Variables : (Disabled)')
    print('\t ==============================================================\n')

    # Measure time
    start_time = datetime.now()

    # ============================================ #
    # Create a Client for Distributed Calculations
    # ============================================ #

    print('\t ===========================================')
    print('\t Running FRICOSIPY simulation on',workers,'cores...')
    print('\t ===========================================\n')

    with LocalCluster(scheduler_port=local_port, n_workers=workers, threads_per_worker = 1, silence_logs = True) as cluster:
        run_cosipy(cluster, IO, STATIC, METEO, ILLUMINATION, RESULT)

    # ================== #
    # Write Result File:
    # ================== #
   
    encoding = dict()
    for var in IO.get_result().data_vars:
        encoding[var] = dict(zlib=True, complevel=compression_level)
  
    IO.get_result().to_netcdf(os.path.join(data_path,'output',output_netcdf), encoding=encoding, mode = 'w')
    
    simulation_time = datetime.now() - start_time
    
    print(f"\n\n\t Total simulation duration: %g hrs %g mins %g secs \n" % (simulation_time.total_seconds()//3660,(simulation_time.total_seconds()%3660)//60,(simulation_time.total_seconds()%3660)%60))
    print('\t =============================')
    print('\t FRICOSIPY Simulation Complete')
    print('\t =============================')

# =============================================================================================================== #

def run_cosipy(cluster, IO, STATIC, METEO, ILLUMINATION, RESULT):

    with Client(cluster) as client:

        # Log cluster and client information:
        print('\t',cluster)
        print('\t',client,'\n')
        sys.stdout.flush()

        # Start simulation timer
        start_time = datetime.now()

        # Create numpy arrays which aggregates all local results
        IO.create_global_result_arrays()

        # Generate a list of the spatial indexes of all glacial nodes: 
        nodes = []
        for y,x in product(range(STATIC.sizes['y']),range(STATIC.sizes['x'])):
            mask = STATIC.MASK.isel(y=y, x=x)
            if mask == 1 :
                nodes.append((y,x))

        # Group nodes according to the number of workers available (i.e. the number that can run simulatenously)
        groups = [nodes[i:i + workers] for i in range(0, len(nodes), workers)]

        # Simulate each group sequentially
        finished = 0
        for i in range(len(groups)):

            # Submit the spatial nodes to each worker and run the FRICOSIPY model
            futures = []
            for y,x in groups[i]:
                futures.append(client.submit(fricosipy_core, STATIC.isel(y=y, x=x), METEO, ILLUMINATION.isel(y=y, x=x), y, x))

            # Main FRICOSIPY Simulation 

            # Write the results collected from each worker to release memory
            for future in as_completed(futures):

                # Get the results from the workers
                indY,indX, \
                AIR_TEMPERATURE,AIR_PRESSURE,RELATIVE_HUMIDITY,WIND_SPEED,FRACTIONAL_CLOUD_COVER, \
                SHORTWAVE,LONGWAVE,SENSIBLE,LATENT,GROUND,RAIN_FLUX,MELT_ENERGY, \
                RAIN,SNOWFALL,EVAPORATION,SUBLIMATION,CONDENSATION,DEPOSITION,SURFACE_MELT,SMB, \
                REFREEZE,SUBSURFACE_MELT,RUNOFF,MB, \
                SNOW_HEIGHT,TOTAL_HEIGHT,SURFACE_TEMPERATURE,SURFACE_ALBEDO,N_LAYERS,FIRN_TEMPERATURE,FIRN_TEMPERATURE_CHANGE,FIRN_FACIE, \
                LAYER_DEPTH,LAYER_HEIGHT,LAYER_DENSITY,LAYER_TEMPERATURE,LAYER_WATER_CONTENT,LAYER_COLD_CONTENT,LAYER_POROSITY,LAYER_ICE_FRACTION, \
                LAYER_IRREDUCIBLE_WATER,LAYER_REFREEZE,LAYER_HYDRO_YEAR = future.result()
                                
                IO.copy_local_to_global(indY,indX, \
                AIR_TEMPERATURE,AIR_PRESSURE,RELATIVE_HUMIDITY,WIND_SPEED,FRACTIONAL_CLOUD_COVER, \
                SHORTWAVE,LONGWAVE,SENSIBLE,LATENT,GROUND,RAIN_FLUX,MELT_ENERGY, \
                RAIN,SNOWFALL,EVAPORATION,SUBLIMATION,CONDENSATION,DEPOSITION,SURFACE_MELT,SMB, \
                REFREEZE,SUBSURFACE_MELT,RUNOFF,MB, \
                SNOW_HEIGHT,TOTAL_HEIGHT,SURFACE_TEMPERATURE,SURFACE_ALBEDO,N_LAYERS,FIRN_TEMPERATURE,FIRN_TEMPERATURE_CHANGE,FIRN_FACIE, \
                LAYER_DEPTH,LAYER_HEIGHT,LAYER_DENSITY,LAYER_TEMPERATURE,LAYER_WATER_CONTENT,LAYER_COLD_CONTENT,LAYER_POROSITY,LAYER_ICE_FRACTION, \
                LAYER_IRREDUCIBLE_WATER,LAYER_REFREEZE,LAYER_HYDRO_YEAR)
                    
                # Write results to file
                IO.write_results_to_file()

                # Update progress bar:
                finished += 1
                report_progress(finished,len(nodes),start_time)

# =============================================================================================================== #
    
def compute_scale_and_offset(min, max, n):
    # stretch/compress data to the available packed range
    scale_factor = (max - min) / (2 ** n - 1)
    # translate the range to be symmetric about zero
    add_offset = min + 2 ** (n - 1) * scale_factor
    return (scale_factor, add_offset)

def report_progress(completed,total_nodes,start_time):
    barLength = 50 # Modify this to change the length of the progress bar
    progress = completed / total_nodes
    time_delta = datetime.now() - start_time
    block = int(round(barLength*progress))
    update = "\t [{0}] | {1} / {2} {3} | {4}% | {5}\n".format( "#"*block + "-"*(barLength-block), completed, total_nodes,
             "Nodes simulated",round(progress*100,2),"%g hrs %g mins %g secs" % (time_delta.total_seconds()//3660,(time_delta.total_seconds()%3660)//60,(time_delta.total_seconds()%3660)%60))
    sys.stdout.write(update)
    sys.stdout.flush()

@gen.coroutine
def close_everything(scheduler):
    yield scheduler.retire_workers(workers=scheduler.workers, close_workers=True)
    yield scheduler.close()

''' MODEL EXECUTION '''
if __name__ == "__main__":
    main()
