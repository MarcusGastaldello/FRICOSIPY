.. image:: https://github.com/user-attachments/assets/dc18f29c-701c-457c-ad65-3257fdf42731

University of FRIbourg variant of the COupled Snow and Ice Model in Python (FRICOSIPY) that specialises in detailed modelling of subsurface firn processes. Developed from COSIPY (Sauter et al., 2020).


:FRICOSIPY Citation:
    .. image:: https://img.shields.io/badge/Citation-TC%20paper-blue.svg
        :target: https://doi.org/10.5194/egusphere-2024-2892

    .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3902191.svg
        :target: http://doi.org/10.5281/zenodo.13361824

:Original COSIPY Model:
    .. image:: https://img.shields.io/badge/Citation-GMD%20paper-orange.svg
        :target: https://gmd.copernicus.org/articles/13/5645/2020/

    .. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2579668.svg
        :target: https://doi.org/10.5281/zenodo.2579668

:License:
    .. image:: https://img.shields.io/badge/License-GPLv3-red.svg
        :target: http://www.gnu.org/licenses/gpl-3.0.en.html

:Support / Contact:
    .. image:: https://img.shields.io/badge/Contact-Marcus%20Gastaldello-blue.svg
        :target: https://www.unifr.ch/directory/en/people/329166/38c19


    .. image:: https://img.shields.io/badge/ORCID-0009%200003%202384%203617-brightgreen.svg
        :target: https://orcid.org/0009-0003-2384-3617

----

Installation
=======


**1.**    Download the latest version of the FRICOSIPY model and unpack its contents from the ZIP archive folder.

**2.**    Navigate to the directory where you have downloaded the FRICOSIPY model in the command prompt using the 'cd' (change directory) command: Eg.

    .. code-block:: console

        cd C:\Users\<username>\Downloads\FRICOSIPY

*Note: it is reccomended to move the model to a more suitable directory.*

**3.**    Create the conda environment. If you do not have *Miniconda* already installed, you must install it first (https://www.anaconda.com/download).

    .. code-block:: console

        conda create --name <env> --file requirements.txt

Henceforth, when running the FRICOSIPY model you must always ensure this new conda environment is active: 

    .. code-block:: console

        conda activate <env>

----

Model Input Files
=======

The FRICOSIPY model requires three input Network Common Data Format (NetCDF) files in order to run a simulation:

1.    Static File
-----------
The model static input file contains topographic information that varies across the spatial domain ( 𝑥 , 𝑦 ) and requires the following variables:

* **NORTHING** - Northing [m]
* **EASTING** - Easting [m]
* **LATITUDE** - Latitude (WGS84) [decimal]
* **LONGITUDE** - Longitude (WGS84) [decimal]
* **ELEVATION** - Elevation [m a.s.l.]
* **ASPECT** - Terrain aspect [°]
* **SLOPE** - Terrain slope [°]
* **MASK** - Glacier mask boolean [0 or 1]

An exemplar static CSV would therefore have the following format:

============  ===========  ============  =============  =============  ==========  =========  ======== 
  NORTHING      EASTING      LATITUDE      LONGITUDE      ELEVATION      ASPECT      SLOPE      MASK  
============  ===========  ============  =============  =============  ==========  =========  ========
  1086500       2633800      45.92925      7.874360        4457.10       240.24      2.35         1
  1086600       2633800      45.93039      7.874485        4456.72       210.12      4.13         1
============  ===========  ============  =============  =============  ==========  =========  ========

*Note: FRICOSIPY requires a standard rectilinear grid.*

The '*create_STATIC.py*' utility program can then convert it into NetCDF format, if required.

    .. code-block:: console

        cd utilities/create_STATIC/
        python3 create_static_netcdf.py -c ../../data/static/<static_csv>.csv -s ../../data/static/<static_netcdf>.nc

*Note: A utility program to directly convert a Digital Elevation Model to a static file is currently in development.*

----

2.    Meteo File
-----------
The model meteorological input file contains the meteorological data varying through time ( 𝑡 ) and requires the following variables:

* **DATETIME** - Datetime [yyyy-mm-dd hh:mm]
* **T2**   - Air temperature [K]
* **U2**   - Wind speed [m s-1]
* **RH2**  - Relative humidity [%]
* **PRES** - Atmospheric pressure [hPa]
* **RRR**  - Precipitation [mm]
* **N**    - Fractional cloud cover [0-1]

Alternatively, instead of using fractional cloud cover ( N ), the user can specify directly measured radiative fluxes:

* **SWin** - Shortwave radiation [W m-2]
* **LWin** - Longwave radiation [W m-2]

An exemplar meteo CSV would therefore have the following format:

====================  ==========  =========  =========  ==========  ========  ========
  DATETIME                T2         U2         RH2        PRES       RRR        N        
====================  ==========  =========  =========  ==========  ========  ========
  2024-01-00 13:00      273.15      6.22       60.54      652.42      1.00      0.32   
  2024-01-00 14:00      274.56      8.71       66.22      672.18      0.00      0.12   
====================  ==========  =========  =========  ==========  ========  ========

The '*create_METEO.py*' utility program can then convert it into NetCDF format, if required.

    .. code-block:: console

        cd utilities/create_METEO/
        python3 create_meteo_netcdf.py -c ../../data/meteo/<meteo_csv>.csv -m ../../data/meteo/<meteo_netcdf>.nc

----

3.    Illumination File
-----------

The model illumination input file determines whether grid nodes across the spatial domain ( 𝑥 , 𝑦 ) are illuminated by the sun for any given timestep in a standard calendar and leap year ( 𝑡 ) :

The '*create_ILLUMINATION.py*' utility program can create this file from an existing static file.

    .. code-block:: console

        cd utilities/create_ILLUMINATION/
        python3 create_illumination_netcdf.py -s ../../data/static/<static_netcdf>.nc -i ../../data/illumination/<illumination_netcdf>.nc

*Note: The illumination file is currently limited to a minimum of an hourly temporal resolution.*

----

Model Setup
=======

Configuration
-----------

In order to run a FRICOSIPY simulation, the user must first appropiately edit the configuration file (*config.py*). This file specifies the model input files and the temporal range of the simulation. For greater customisation of the output dataset, the user can also control the output reporting frequency and specify which variables are to be written into the output dataset. 

Parallelisation
-----------

For improved computational efficiency, FRICOSIPY supports parallel computing using the *Dask Distributed* package; multiple grid nodes can therefore be simulated simultaneously. Within '*config.py*', users can modify the number of workers/processers used in the simulation, however be mindful that memory (RAM) must be shared between the processors. 

Parameters & Paremeterisations
-----------

The '*parameters.py*' controls all parameters of the model's physical processes - these should be carefully selected and calibrated to site conditions before running a simulation. For more advanced users, there are a selection of alternative parameterisations that can be selected for enhanced model versatility.


----

Running the FRICOSIPY Simulation
=======

Finally, to run the FRICOSIPY simulation, type the following into the command line from the main model directory:

    .. code-block:: console

        python3 FRICOSIPY.py

When initialising, key simulation information will be printed in the terminal. Subsequently, progress updates will be received as nodes simulate until the simulation finishes.

----




































