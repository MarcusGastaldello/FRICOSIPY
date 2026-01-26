---
og_title: FRICOSIPY | Parameters 
og_description: A brief guide to optimum parameter selection for a FRICOSIPY simulation
---

# Parameters

For any *FRICOSIPY* simulation, it is important to properly customise the model's parameters and parameterisations by modifying the file: `parameters.py`. 

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Model Parameterisations

The *FRICOSIPY* model enables the user to customise the parameterisations used to model key physical processes.  The following tables provide links to the original source literature of the paramterisations and the section of this documentation that explains its implementation in the model.

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
| [**Precipitation**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#precipitation) | Standard | [Mattea et al. (2021)](https://doi.org/10.5194/tc-15-3181-2021) |
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
    If you have any reccomendations for improved or alternative parameterisations, [please contact the model developers](https://fricosipy.readthedocs.io/en/latest/contact/). The modular design of *FRICOSIPY* means that it is relatively straightforward to add new parameterisations into the model for upcoming releases.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Model Parameters
<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### General Model Parameters

| Parameter | Value | Units | Description |
|:---|:---:|:---:|---|
| `dt`          | <small>3600</small> | s | Simulation time step |
| `max_depth`   | <small>50</small>   | m | Maximum simulation depth |
| `max_layers`  | <small>500</small>  | – | Maximum number of subsurface layers |

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Meteorological Input Parameters

| Parameter | Value | Units | Description |
|-----|:---:|:---:|---|
| `station_altitude` | <small>3000.0</small>            | m a.s.l. | Altitude of meteorological station |
| `z` | <small>2.0</small>                              | m | Meteorological data measurement height |
| `air_temperature_lapse_rate` | <small>-0.006</small>  | K m$^{-1}$ | Air temperature lapse rate |
| `precipitation_lapse_rate` | <small>0.0002</small>    | % m$^{-1}$ | Precipitation lapse rate |
| `precipitation_multiplier` | <small>1.0</small>       | – | Multiplicative scaling factor for precipitation data |
| `minimum_snowfall` | <small>0.00001</small>           | m | Minimum snowfall per simulation timestep |

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Physical Processes Parameters

| Parameter | Value | Units | Description |
|:---|:---:|:---:|---|
| `albedo_fresh_snow` | <small>0.85</small>                        | – | Albedo of fresh snow |
| `albedo_firn` | <small>0.52</small>                              | – | Albedo of firn |
| `albedo_ice` | <small>0.30</small>                               | – | Albedo of ice |
| `albedo_characteristic_snow_depth` | <small>3.0</small>          | cm | Characteristic scale for snow depth |
| `cloud_transmissivity_coeff_alpha` | <small>0.233</small>        | – | Cloud transmissivity coefficient alpha |
| `cloud_transmissivity_coeff_beta` | <small>0.415</small>         | – | Cloud transmissivity coefficient beta |
| `cloud_emissivity` | <small>0.96</small>                         | – | Emissivity of clouds |
| `LW_emission_constant` | <small>0.42</small>                     | – | Constant in the longwave emission formula |
| `subsurface_interpolation_depth_1` | <small>0.06</small>         | m | First depth for temperature interpolation which is used for calculation of subsurface/ground heat flux |
| `subsurface_interpolation_depth_2` | <small>0.10</small>         | m | Second depth for temperature interpolation which is used for calculation of subsurface/ground heat flux |
| `basal_heat_flux` | <small>35</small>                            | mW m$^{-2}$ | Basal / Geothermal heat flux |
| `pore_close_off_density` | <small>830.0</small>                  | kg m$^{-3}$ | Pore close-off density |
| `snow_ice_threshold` | <small>900.0</small>                      | kg m$^{-3}$ | Snow-ice density threshold |
| `surface_emission_coeff` | <small>1.0</small>                    | – | Surface emission coefficient for snow/ice |
| `firn_temperature_depth` | <small>20.0</small>                   | m | Depth at which firn temperature is measured |
| `grain_size_fresh_snow` | <small>0.1</small>                     | mm | Grain size of fresh snow |

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Parameterisation-choice specifc Parameters

| Parameter | Value | Units | Description |
|:---|:---:|:---:|---|
| `extinction_coeff_snow` | <small>17.1</small>                    | m$^{-1}$ | *(Bintanja & van den Broeke, 1998)* Extinction coefficient for snow |
| `extinction_coeff_ice` | <small>2.5</small>                      | m$^{-1}$ | *(Bintanja & van den Broeke, 1998)* Extinction coefficient for ice |
| `albedo_decay_timescale` | <small>22</small>                     | days | *(Oerlemans & Knap, 1998)* Albedo decay timescale (constant) |
| `albedo_decay_timescale_wet` | <small>10</small>                 | days | *(Bougamont et al., 2005)* Albedo decay timescale (melting surface) |
| `albedo_decay_timescale_dry` | <small>30</small>                 | days | *(Bougamont et al., 2005)* Albedo decay timescale (dry snow surface) |
| `albedo_decay_timescale_dry_adjustment` | <small>14</small>      | day K$^{-1}$ | *(Bougamont et al., 2005)* Albedo dry snow decay timescale increase at negative temperatures |
| `albedo_decay_timescale_threshold` | <small>263.17</small>       | K | *(Bougamont et al., 2005)* Albedo temperature threshold for dry snow decay timescale increase |
| `surface_roughness_fresh_snow` | <small>0.24</small>             | mm | *(Moelg et al., 2012)* Surface roughness length for fresh snow |
| `surface_roughness_ice` | <small>1.7</small>                     | mm | *(Moelg et al., 2012)* Surface roughness length for ice |
| `surface_roughness_firn` | <small>4.0</small>                    | mm | *(Moelg et al., 2012)* Surface roughness length for aged snow |
| `surface_roughness_timescale` | <small>0.0026</small>            | hours | *(Moelg et al., 2012)* Roughness length timescale |
| `constant_fresh_snow_density` | <small>250.</small>              | kg m$^{-3}$ | *(Constant - snow_density_method)* Constant density of freshly fallen snow |
| `constant_surface_roughness` | <small>0.001</small>              | m | *(Constant - surface_roughness_method)* Surface roughness constant |
| `preferential_percolation_depth` | <small>3.0</small>            | m | *(Marchenko et al., 2017)* Characteristic preferential percolation depth |
| `constant_irreducible_water_content` | <small>0.02</small>       | - | *(Constant - irreducible_water_content_method)* Constant irreducible water content |
| `temperature_interpolation_depth_1` | <small>10</small>          | m | *(Ligtenberg et al., 2011)* First depth for temperature interpolation which is used for calculation of average subsurface layer temperature |
| `temperature_interpolation_depth_2` | <small>20</small>          | m | *(Ligtenberg et al., 2011)* Second depth for temperature interpolation which is used for calculation of average subsurface layer temperature |

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Subsurface Remeshing Options

The subsurface remeshing options allow the user to modify the resolution of the subsurface grid.

| Parameter | Value | Units | Description |
|:---|:---:|:---:|---|
| `minimum_snow_layer_height` | <small>0.0005</small>            | m | Minimum layer height |
| `maximum_simulation_layer_height` | <small>0.10</small>        | m | Maximum height of fine layers |
| `maximum_coarse_layer_height` | <small>0.3</small>             | m | Maximum height of coarse layers |
| `coarse_layer_threshold` | <small>21.</small>                  | m | Threshold depth at which fine near-surface layers are merged into coarser deep layers |

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Initial Conditions

The initial condition parameters control how the subsurface grid is initialised at the start of the simulation.

| Parameter | Value | Units | Description |
|:---|:---:|:---:|---|
| `initial_snowheight` | <small>2.00</small>                    | m | Initial snowheight |
| `initial_snow_layer_heights` | <small>0.10</small>            | m | Initial thickness of snow layers |
| `initial_snow_grain_size` | <small>0.10</small>               | mm | Initial snow grain size |
| `initial_ice_grain_size` | <small>5.0</small>                 | mm | Initial ice grain size |
| `initial_glacier_height` | <small>50.0</small>                | m | Initial glacier height (without snowlayers) |
| `initial_glacier_layer_heights` | <small>1.0</small>          | m | Initial thickness of glacier ice layers |
| `initial_upper_snowpack_density` | <small>250.0</small>       | kg m$^{-3}$  | Top density for initial snowpack |
| `initial_lower_snowpack_density` | <small>275.0</small>       | kg m$^{-3}$  | Bottom density for initial snowpack |
| `initial_upper_temperature` | <small>270.16</small>           | K | Upper boundary condition for initial temperature profile |
| `initial_lower_temperature` | <small>273.16</small>           | K | Lower boundary condition for initial temperature profile |

!!! note
    For detailed subsurface investigations, it is strongly reccomended to precede the main simulation with a spin-up/initialisation phase; otherwise, the initial years of the simulation will be heavily influenced by these arbitrary initial conditions.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
