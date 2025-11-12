# Model Input Files

The *FRICOSIPY* model requires three input *Network Common Data Format* (NetCDF) files in order to run a simulation: *Static*, *Meteo* and *Illumination*. These replace the large 3-dimensional input dataset ( 𝑥 , 𝑦 , 𝑡 ) of the original *COSIPY* model in order to lessen the required computational resources and enable the execution of a simulation with a high spatio-temporal resolution.

---

## Static

The model static input file contains topographic information that varies across the spatial domain  
( 𝑥 , 𝑦 ) and requires the following variables:

* **NORTHING** - Northing [m]
* **EASTING** - Easting [m]
* **LATITUDE** - Latitude (WGS84) [decimal]
* **LONGITUDE** - Longitude (WGS84) [decimal]
* **ELEVATION** - Elevation [m a.s.l.]
* **ASPECT** - Terrain aspect [°]
* **SLOPE** - Terrain slope [°]
* **MASK** - Glacier mask boolean [0 or 1]

An exemplar static CSV would therefore have the following format:

| NORTHING | EASTING | LATITUDE | LONGITUDE | ELEVATION | ASPECT | SLOPE | MASK |
|-----------|----------|-----------|------------|------------|---------|--------|------|
| 1086500 | 2633800 | 45.92925 | 7.874360 | 4457.10 | 240.24 | 2.35 | 1 |
| 1086600 | 2633800 | 45.93039 | 7.874485 | 4456.72 | 210.12 | 4.13 | 1 |

!!! note
    FRICOSIPY requires a standard rectilinear grid.

The '*create_STATIC.py*' utility program can then convert it into NetCDF format, if required.

```python
cd utilities/create_STATIC/
python3 create_static_netcdf.py -c ../../data/static/<static_csv>.csv -s ../../data/static/<static_netcdf>.nc
```

!!! note
     A utility program designed to directly convert a Digital Elevation Model (DEM) to a static file (without the need for GIS software)
     is currently in development.

---

## Meteo

---

## Illumination

---
