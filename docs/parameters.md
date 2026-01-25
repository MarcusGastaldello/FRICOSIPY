---
og_title: FRICOSIPY | Parameters 
og_description: A brief guide to optimum parameter selection for a FRICOSIPY simulation
---

# Parameters

For any *FRICOSIPY* simulation, it is important to properly customise the model's parameters and parameterisations by modifying the file: `parameters.py`. 

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Model Parameterisations

The *FRICOSIPY* model enables the user to customise the parameterisations used to model key physical processes.

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Surface Energy Balance

| Parameterisation | Default method | Alternative methods |
|---|---|---|
| [**Surface albedo**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#albedo-parameterisations) | [Oerlemans & Knap (1998)](https://doi.org/10.3189/S0022143000002574) | [Bougamont et al. (2005)](https://doi.org/10.1029/2005JF000348) | 
| [**Penetrating radiation**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#penetrating-radiation-parameterisation) | [Bintanja & van den Broeke (1998)](https://doi.org/10.1175/1520-0450(1995)034<0902:TSEBOA>2.0.CO;2) | Disabled | 
| [**Surface roughness**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#surface-roughness-parameterisation) | [Moelg et al. (2012)](https://doi.org/10.5194/tc-6-1445-2012) | Constant | 
| [**Saturation vapour pressure**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#saturation-vapour-pressure-parameterisation) | [Sonntag (1994)](https://doi.org/10.1127/metz/3/1994/51) | *(None)* | 
| [**Incoming longwave radiation**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#longwave-radiation-parameterisation) | [Konzelmann (1994)](https://doi.org/10.1016/0921-8181(94)90013-2) | *(None)* |
| [**Surface temperature solver**](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/#) | *Newton* | *L-BFGS-B* or *SLSQP* | 

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Multi-layer Subsurface Model

| Parameterisation | Default method | Alternative methods |
|---|---|---|
| [**Precipitation**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#precipitation) | Standard | Three-phase anomaly|
| [**Fresh snow density**]() | Constant | [Vionnet et al. (2012)](https://doi.org/10.5194/gmd-5-773-2012) |
| [**Thermal conductivity**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#thermal-conductivitiy-parameterisations) | Bulk-volumetric | [Sturm (1997)](https://doi.org/10.3189/S0022143000002781) or <br> [Calonne et al. (2019)](https://doi.org/10.1029/2019GL085228) |
| [**Specific heat capacity**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#specific-heat-capacity-parameterisations) | Bulk-volumetric | [Yen (1981)](https://apps.dtic.mil/sti/citations/ADA103734) |
| [**Standard percolation**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#percolation-refreezing) | Bucket | [Darcy (Hirashima et al., 2010)](https://doi.org/10.1016/j.coldregions.2010.09.003) |
| [**Preferential percolation**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#preferential-percolation-parameterisations) | Disabled | [Marchenko et al. (2017)](https://doi.org/10.3389/feart.2017.00016) |
| [**Hydraulic conductivity**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#hydraulic-conductivitiy-parameterisations) | [Calonne et al. (2012)](https://doi.org/10.5194/tc-6-939-2012) | [Shimzu (1970)](https://hdl.handle.net/2115/20234) |
| [**Irreducible water content**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#irreducible-water-content-parameterisations) | [Coléou and Lesaffre (1998)](https://doi.org/10.3189/1998AoG26-1-64-68)| Constant |
| [**Dry densification**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#firn-densification-parameterisations) | [Anderson (1976)]() | [Ligtenberg et al. (2011)](https://doi.org/10.5194/tc-5-809-2011) |
| [**Snow metamorphism**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#snow-metamorphism-parameterisations) | [Katsushima et al. (2009)](https://doi.org/10.1016/j.coldregions.2009.09.002) | *(None)* | 

!!! note
    If you have any reccomendations for improved or alternative parameterisations, please contact the model developers. The modular design of *FRICOSIPY* means that it is relatively straightforward to add new parameterisations into the model for upcoming releases.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Model Parameters
<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### General Model Parameters

| Parameter | Units | Description |
|-----|:---:|---|
| `dt = 3600`         | s | Simulation time step |
| `max_depth = 50`    | m | Maximum simulation depth |
| `max_layers = 500`  | – | Maximum number of subsurface layers |

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Meteorological Input Parameters

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Physical Processes Parameters

A

<div style="overflow-x: auto; white-space: nowrap;">

| Parameter | Units | Description |
|:--------------------------------------------------------------------------------------------------------------|:---:|---|
| `albedo_fresh_snow = 0.85`                        | – | Albedo of fresh snow |
| `albedo_firn = 0.52`                              | – | Albedo of firn |
| `albedo_ice = 0.30`                               | – | Albedo of ice |
| `albedo_characteristic_snow_depth = 3.0`          | cm | Characteristic scale for snow depth |
| `cloud_transmissivity_coeff_alpha = 0.233`        | – | Cloud transmissivity coefficient alpha |
| `cloud_transmissivity_coeff_beta = 0.415`         | – | Cloud transmissivity coefficient beta |
| `cloud_emissivity = 0.96`                         | – | Emissivity of clouds |
| `LW_emission_constant = 0.42`                     | – | Constant in the longwave emission formula |
| `subsurface_interpolation_depth_1 = 0.06`         | m | First depth for temperature interpolation which is used for calculation of subsurface/ground heat flux |
| `subsurface_interpolation_depth_2 = 0.10`         | m | Second depth for temperature interpolation which is used for calculation of subsurface/ground heat flux |
| `basal_heat_flux = 35`                            | mW m$^{-2}$ | Basal / Geothermal heat flux |
| `pore_close_off_density = 830.0`                  | kg m$^{-3}$ | Pore close-off density |
| `snow_ice_threshold = 900.0`                      | kg m$^{-3}$ | Snow-ice density threshold |
| `surface_emission_coeff = 1.0`                    | – | Surface emission coefficient for snow/ice |
| `firn_temperature_depth = 20.0`                   | m | Depth at which firn temperature is measured |
| `grain_size_fresh_snow = 0.1`                     | mm | Grain size |

</div>

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Parameterisation-choice specifc Parameters

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Subsurface Remeshing Options

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Initial Conditions

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
