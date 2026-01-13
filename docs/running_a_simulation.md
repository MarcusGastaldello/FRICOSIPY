---
og_title: FRICOSIPY | Running a Simulation
og_description: An explanation of how to setup the configuration file and run a simulation.
---

# Running a Simulation

In order to run the *FRICOSIPY* model, the user must first configure the simulation by editing the configuration file: `config.py`

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## File Selection

For each simulation, the user must specify the three model input files and the desired name of the output file.

!!! note
    It is only necessary to specify the filename of the input static, meteo & illumination files; 

    to their respective folders in the *data/* directory – the same directory in which the model input file creation programs (eg. `create_meteo_netcdf.py`) will have placed them.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Spatial Extent / Subset



bounding box



<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Output Variables

The *FRICOSIPY* model reports a large selection of variables into the output NetCDF dataset. The user can (de)select any of these variables in the configuration file. 

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### 3-D Output Variables ( $𝑥$ , $𝑦$ , $t$ )

The *FRICOSIPY* model will report the following variables for each spatial node $(x,y)$ for every simulation timestep $(t)$:

**Meteorological Variables $(5)$**
    
| Variable | Description | Unit |
|:---|:---|:---:|
| **AIR_TEMPERATURE** | Air temperature | °C |
| **AIR_PRESSURE** | Barometric air pressure | hPa |
| **RELATIVE_HUMIDITY** | Relative humidity | % |
| **WIND_SPEED** | Wind speed | m s$^{-1}$ |
| **FRACTIONAL_CLOUD_COVER** | Fractional cloud cover | — |

---

**Surface Energy Fluxes $(7)$**
    
| Variable | Description | Unit |
|:---|:---|:---:|
| **SHORTWAVE** | Net shortwave radiation flux | W m$^{-2}$ |
| **SENSIBLE** | Net sensible radiation flux | W m$^{-2}$ |
| **LATENT** | Net latent radiation flux | W m$^{-2}$ |
| **LONGWAVE** | Net longwave radiation flux | W m$^{-2}$ |
| **RAIN_HEAT** | Rain heat flux | W m$^{-2}$ |
| **SUBSURFACE** | Subsurface heat flux | W m$^{-2}$ |
| **MELT_ENERGY** | Melt energy flux | W m$^{-2}$ |

---

**Surface Mass Fluxes $(8)$**

| Variable | Description | Unit |
|:---|:---|:---:|
| **RAIN** | Rain | m w.e. |
| **SNOWFALL** | Snowfall | m w.e. |
| **EVAPORATION** | Evaporation | m w.e. |
| **SUBLIMATION** | Sublimation | m w.e. |
| **CONDENSATION** | Condensation | m w.e. |
| **DEPOSITION** | Deposition | m w.e. |
| **SURFACE_MELT** | Surface melt | m w.e. |
| **SURFACE_MASS_BALANCE** | Surface mass balance | m w.e. |

---

**Subsurface Mass Fluxes $(4)$**

| Variable | Description | Unit |
|:---|:---|:---:|
| **REFREEZE** | Refreezing | m w.e. |
| **SUBSURFACE_MELT** | Subsurface melt | m w.e. |
| **RUNOFF** | Runoff | m w.e. |
| **MASS_BALANCE** | Mass balance | m w.e. |

---

**Other $(9)$**

| Variable | Description | Unit |
|:---|:---|:---:|
| **SNOW_HEIGHT** | Snow height | m |
| **SNOW_WATER_EQUIVALENT** | Snow water equivalent | m w.e. |
| **TOTAL_HEIGHT** | Total height | m |
| **SURFACE_ELEVATION** | Surface elevation | m a.s.l. |
| **SURFACE_TEMPERATURE** | Surface temperature | $^\circ$C |
| **SURFACE_ALBEDO** | Surface albedo | — |
| **N_LAYERS** | Number of layers | — |
| **FIRN_TEMPERATURE \*** | Firn temperature | $^\circ$C |
| **FIRN_TEMPERATURE_CHANGE \*** | Firn temperature change | $^\circ$C $^{-1}$ |
| **FIRN_FACIE \*** | Firn Facie (acc. [Shumskii, 1964](https://doi.org/10.1017/S0016756800050597)) <br> 0 : Recrystillisation (dry snow) <br> 1 : Recrystallisation-infiltration <br> 2 : Cold-infiltration <br> 3 : Warn-infiltration (temperate)| — |

<small> *( \* Note: Firn temperatures and facies are evaluated at the depth prescribed by the `firn_temperature_depth` parameter. )* </small>

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### 4-D Output Variables ( $x$ , $𝑦$ , $z$ , $t$  )

If the user sets `full_field == True`, then the *FRICOSIPY* model will also report the following subsurface variables for every layer $(z)$:

**Subsurface Variables $(12)$**
    
| Variable | Description | Unit |
|:---|:---|:---:|
| **DEPTH** | Layer depth | m |
| **HEIGHT** | Layer height | m |
| **DENSITY** | Layer density | kg m$^{-3}$ |
| **TEMPERATURE** | Layer temperature | $^\circ$C |
| **WATER CONTENT** | Layer volumetric water content | — |
| **COLD CONTENT** | Layer cold content | J m$^{-2}$ |
| **POROSITY** | Layer volumetric porosity | — |
| **ICE FRACTION** | Layer volumetric ice fraction | — |
| **IRREDUCIBLE WATER** | Layer irreducible water content | — |
| **REFREEZE** | Layer refreeze | m w.e. |
| **HYDRO YEAR** | Layer hydrological year | yyyy |
| **GRAIN SIZE** | Layer grain size | mm |
    
!!! note
    Including the subsurface variables greatly increases the size of the output dataset and the amount of memory required by the simulation. It is therefore reccomended that the user sets `full_field = false` *(default)*, unless they specifically require the data.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Output Reporting Frequency

By default, as with the original *COSIPY* model, *FRICOSIPY* reports each output variable for every simulation timestep. However, this can produce extremely large output datasets when operating with a long simulation time period. Therefore, the *FRICOSIPY* model offers a few methods to customise the reporting frequency for the output dataset. 

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### $(i)$ Model Initialisation / Spin-up

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### $(ii)$ Output Timestamps

Alternatively, the user can directly specify the output timestamps on which the simulation reports output variables. The user must simply set `reduced_output == True` and place a CSV with the desired timestamps, expressed in datetime format [yyyy-mm-dd hh:mm], in the *data/output/output_timestamps/* directory. Inbetween the reported values, variables are aggregated: meteorological conditions and energy fluxes are averaged, mass fluxes are summated and state variables are reported as their instantaneous values.

<small> *Ex. An exemplar output timestamps file showing yearly timestamps for the time period 2000 – 2025, which would reduce the output dataset from 219,150 hourly values to 25 aggregated annual values.* </small>

|          |
|:---:|
| 2000-12-31 23:00   |
| 2001-12-31 23:00   |
| ⋮ |
| 2024-12-31 23:00   |
| 2025-12-31 23:00   |

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Dask Parallelisation

The *FRICOSIPY* model, supports multi-thread processing using the *Dask* parallel computing library. By modifying `workers = 1`, the user specifies the number of spatial nodes that the simulation will concurrently simulate

!!! warning
    When multi-threading / parallelisation is activated, the total available Random Access Memory (RAM) of your computer is divided between each worker. If insufficient memory is allocated to each worker, the simulation will crash. The user should carefully examine whether they have sufficient memory available for their simulation; those with a large large output dataset will inherently require more memory. Consider reducing the output reporting frequency, using a smaller spatial subset or disabling the reporting of ubsurface variables. 

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

# Executing a Simulation

Once the configuration file is set up, the *FRICOSIPY* model is executed with the command:

```
python FRICOSIPY.py
```

As the simulation starts, detailed information will be reported into the terminal. Thereafter, progress will be indicated upon the completion of each spatial node until the simulation is complete. 

!!! attention
    Remember that your conda environment must be active `conda activate <env>` and you must be in the directory of the FRICOSIPY model.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
