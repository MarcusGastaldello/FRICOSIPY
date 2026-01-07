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

??? "**Meteorological Variables (5)**"

    <div style="height: 0px;"></div>
    
    | Variable | Description | Unit |
    |:---|:---|:---:|
    | **SHORTWAVE** | Net shortwave radiation flux | W m$^{-2}$ |
    | **SENSIBLE** | Net sensible radiation flux | W m$^{-2}$ |
    | **LATENT** | Net latent radiation flux | W m$^{-2}$ |
    | **LONGWAVE** | Net longwave radiation flux | W m$^{-2}$ |
    | **RAIN HEAT** | Rain heat flux | W m$^{-2}$ |

---

??? "**Surface Energy Fluxes (7)**"

    <div style="height: 0px;"></div>
    
    | Variable | Description | Unit |
    |:---|:---|:---:|
    | **SHORTWAVE** | Net shortwave radiation flux | W m$^{-2}$ |
    | **SENSIBLE** | Net sensible radiation flux | W m$^{-2}$ |
    | **LATENT** | Net latent radiation flux | W m$^{-2}$ |
    | **LONGWAVE** | Net longwave radiation flux | W m$^{-2}$ |
    | **RAIN HEAT** | Rain heat flux | W m$^{-2}$ |
    | **SUBSURFACE** | Subsurface heat flux | W m$^{-2}$ |
    | **MELT ENERGY** | Melt energy flux | W m$^{-2}$ |

---

??? "**Surface Mass Fluxes (8)**"



---

??? "**Subsurface Mass Fluxes (4)**"


---

??? "**Other (9)**"

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### 4-D Output Variables ( $x$ , $𝑦$ , $z$ , $t$  )

??? "**Subsurface Variables (12)**"

    <div style="height: 0px;"></div>
    
    | Variable | Description | Unit |
    |:---|:---|:---:|
    | **DEPTH** | Layer depth | m |
    | **HEIGHT** | Layer height | m |
    | **DENSITY** | Layer density | kg m$^{-3}$ |
    | **TEMPERATURE** | Layer temperature | $^\circ$C |
    | **WATER CONTENT** | Layer volumetric water content | – |
    | **COLD CONTENT** | Layer cold content | J m$^{-2}$ |
    | **POROSITY** | Layer volumetric porosity | – |
    | **ICE FRACTION** | Layer volumetric ice fraction | – |
    | **IRREDUCIBLE WATER** | Layer irreducible water content | – |
    | **REFREEZE** | Layer refreeze | m w.e. |
    | **HYDRO YEAR** | Layer hydrological year | yyyy |
    | **GRAIN SIZE** | Layer grain size | mm |
    
    !!! note
        Including the subsurface variables in the output dataset 

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Output Reporting Frequency

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Dask Parallelisation

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
