# Model Input Files

The *FRICOSIPY* model requires three input *Network Common Data Format* (NetCDF) files in order to run a simulation: *Static*, *Meteo* and *Illumination*. These replace the large 3-dimensional input dataset ( 𝑥 , 𝑦 , 𝑡 ) of the original *COSIPY* model in order to lessen the required computational resources and enable the execution of a simulation with a high spatio-temporal resolution.

---

## Static

The model static input file contains topographic information that varies across the spatial domain  
( 𝑥 , 𝑦 ) and requires the following variables:


The '*create_STATIC.py*' utility program can then convert it into NetCDF format, if required.

```python
cd utilities/create_STATIC/
python3 create_static_netcdf.py -c ../../data/static/<static_csv>.csv -s ../../data/static/<static_netcdf>.nc
```

!!! note
     A utility program to directly convert a Digital Elevation Model to a static file is currently in development.

---

## Meteo

---

## Illumination

---
