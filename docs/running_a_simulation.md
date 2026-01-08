---
# Metadata
og_title: FRICOSIPY | Running a Simulation
og_description: An explanation of how to setup the configuration file and run a simulation.
---

# Running a Simulation


<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## File Selection






## Spatial Extent / Subset

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Output Variables

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### 3-D Output Variables ( $𝑥$ , $𝑦$ , $t$ )

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
| **SURFACE_TEMPERATURE** | Surface temperature | $^\circ$C |
| **SURFACE_ALBEDO** | Surface albedo | — |
| **N_LAYERS** | Number of layers | — |
| **FIRN_TEMPERATURE** | Firn temperature | $^\circ$C |
| **FIRN_TEMPERATURE_CHANGE** | Firn temperature change | $^\circ$C $^{-1}$ |
| **FIRN_FACIE** | Firn Facie | — |

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### 4-D Output Variables ( $x$ , $𝑦$ , $z$ , $t$  )

If ```python `full_field = True` then 

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
    Including the subsurface variables greatly increases the size of the output dataset and the amount of memory required by the simulation.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Output Reporting Frequency

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Dask Parallelisation

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
