---
og_title: FRICOSIPY | Parameters 
og_description: A brief guide to optimum parameter selection for a FRICOSIPY simulation
---

# Parameters

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
| [**Precipitation**](https://fricosipy.readthedocs.io/en/latest/subsurface_model/#precipitation) |  | |
| [**Fresh snow density**]() | Standard | Three-phase anomaly |
| [**Thermal conductivity**]() | Bulk-volumetric | [Sturm (1997)](https://doi.org/10.3189/S0022143000002781) or <br> [Calonne et al. (2019)](https://doi.org/10.1029/2019GL085228) |
| [**Specific heat capacity**]() | Bulk-volumetric | [Yen (1981)](https://apps.dtic.mil/sti/citations/ADA103734) |
| [**Standard percolation**]() | Bucket | [Darcy (Hirashima et al., 2010)](https://doi.org/10.1016/j.coldregions.2010.09.003) |
| [**Preferential percolation**]() | Disabled | [Marchenko et al. (2017)](https://doi.org/10.3389/feart.2017.00016) |
| [**Hydraulic conductivity**]() | | |
| [**Irreducible water content**]() | | |
| [**Dry densification**]() | [Anderson (1976)]() | [Ligtenberg et al. (2011)](https://doi.org/10.5194/tc-5-809-2011) |
| [**Snow metamorphism**]() | [Katsushima et al. (2009)](https://doi.org/10.1016/j.coldregions.2009.09.002) | *(None)* | 

!!!
    
    If you have any reccomendations for improved or alternative parameterisations, please contact the model developers. The modular design of *FRICOSIPY* means that it is relatively straightforward to add new parameterisations into the model for upcoming releases.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Model Parameters
<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### General Model Parameters

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Meteorological Input Parameters

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Physical Processes Parameters

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Parameterisation-choice specifc Parameters

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Subsurface Remeshing Options

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Initial Conditions

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
