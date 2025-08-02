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

**2.**    Navigate to the directory where you have downloaded the FRICOSIPY model in the command prompt using the 'cd' (change directory) command:

    .. code-block:: console

        cd C:\Users\<username>\Downloads\FRICOSIPY

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

1.    Static
-----------
The model static input file contains topographic information that varies across the spatial domain ( 𝑥 , 𝑦 ) and requires the following variables:

* **NORTHING**
* **EASTING**
* **LATITUDE**
* **LONGITUDE**

An exemplar static CSV would therefore have the following format:

============  =====  =======
  NORTHING      B    A and B
============  =====  =======
False         False  False
True          False  False
False         True   False
True          True   True
============  =====  =======

The '*create_STATIC.py*' utility program can then convert it into NetCDF format.

    .. code-block:: console

        cd utilities/create_STATIC/
        python3 create_static_netcdf.py -c ../../data/static/<static_csv>.csv -s ../../data/static/<static_netcdf>.nc

*Note: A utility program to directly convert a Digital Elevation Model to a static file is currently in development.*

----

2.    Meteo
-----------
The model meteorological input file contains the meteorological data varying through time ( 𝑡 ) and requires the following variables:

* **T2**
* **U2**
* **RH2**
* **PRES**
* **RRR**
* **N**

Alternatively, instead of using fractional cloud cover ( N ), the user can specify directly measured radiative fluxes:

* **SWin**
* **LWin**

An exemplar meteo CSV would therefore have the following format:

============  =====  =======
  NORTHING      B    A and B
============  =====  =======
False         False  False
True          False  False
False         True   False
True          True   True
============  =====  =======

The '*create_METEO.py*' utility program can then convert it into NetCDF format.

    .. code-block:: console

        cd utilities/create_METEO/
        python3 create_meteo_netcdf.py -c ../../data/meteo/<meteo_csv>.csv -m ../../data/meteo/<meteo_netcdf>.nc

----

3.    Illumination
-----------

The model illumination input file determines whether grid nodes across the spatial domain ( 𝑥 , 𝑦 ) are illuminated by the sun for any given timestep in a standard calendar and leap year ( 𝑡 ) :

The '*create_ILLUMINATION.py*' utility program can create this file from an existing static file.

    .. code-block:: console

        cd utilities/create_ILLUMINATION/
        python3 create_illumination_netcdf.py -s ../../data/static/<static_netcdf>.nc -i ../../data/illumination/<illumination_netcdf>.nc

*Note: The illumination file is currently limited to a minimum of an hourly temporal resolution.*

----

Running a Simulation
=======




To run the FRICOSIPY simulation, simply type the following into the command line from the FRICOSIPY model directory:

    .. code-block:: console

        python3 FRICOSIPY.py

----


























