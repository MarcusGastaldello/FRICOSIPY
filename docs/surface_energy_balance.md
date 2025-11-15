# Surface Energy Balance

Driven by the input meteorological data, the surface energy fluxes are evaluated at an infinitesimal skin layer to ascertain the surface temperature ($T_s$). Based on the principles of energy conservation:

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9;">
$$
SW_{net} \pm Q_{sensible} \pm Q_{latent} \pm LW_{net} + Q_{rain} \pm Q_{subsurface} = 0
$$
</div>

<small>where $SW_{net}$  is the net shortwave radiation flux, $Q_{sensible}$  and $Q_{latent}$  are the turbulent fluxes for sensible and latent exchange respectively, $LW_{net}$  is the net longwave radiation flux, $Q_{rain}$  is the rain heat flux and $Q_{subsurface}$  is the subsurface heat conduction flux.</small>

![Alt text](images/FRICOSIPY_SEB.png)

<small> **Figure 2**: FRICOSIPY Surface Energy Balance </small>

The *FRICOSIPY* model uses an iterative approach to equalise the energy fluxes; the user can select either a Limited-memory *Broyden*–*Fletcher*–*Goldfarb*–*Shanno* algorithm (L-BFGS) algorithm, the Sequential Least SQuares Programming (SLSQP) approach or the *Newton*-*Raphson* method.

However, since the surface temperature of a glacier is physically constrained to 0 $^\circ$C, excess energy must be apportioned to melt ($Q_{melt}$) should this situation arise.

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9;">
$$
SW_{net} \pm Q_{sensible} \pm Q_{latent} \pm LW_{net} + Q_{rain} \pm Q_{subsurface} = Q_{melt}
$$
</div>
<div style="height: 20px;"></div>
The following section explains each of these energy fluxes in greater detail and how they are parameterised in the *FRICOSIPY* model.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #E86853; border: 2px solid #404040; border-radius: 4px; "></span>  Shortwave Radiation

### Albedo Parameterisations 

#### (a) Oerlemans & Knapp 1998

---

#### (b) Bougamont et al., 2005

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Penetrating Radiation Parameterisations 

#### (a) Bintanja & van den Broeke 1995

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Turbulent Fluxes

### <span style="display: inline-block; width: 1em; height: 1em;background-color: #F99F6C; border: 2px solid #404040; border-radius: 4px; "></span> Sensible Heat Flux

### <span style="display: inline-block; width: 1em; height: 1em;background-color: #9FCBE1; border: 2px solid #404040; border-radius: 4px; "></span> Latent Heat Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #74A0CB; border: 2px solid #404040; border-radius: 4px; "></span> Longwave Radiation

Net longwave radiation is calculated in accordance with the Stefan–Boltzmann law for grey body emission:





If the user is unable to provide incoming longwave radiation ($LW_{in}$) in the input meterological data, it can instead by derived from the fractional cloud cover ($N$) using the parametersiations of Konzelmann et al., 1994. This substitutes the air temperature ($T_a$) and atmospheric emissivity ($\varepsilon_{atm}$) into the *Stefan*-*Boltzmann* law:


<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #ACA9D0; border: 2px solid #404040; border-radius: 4px; "></span> Rain Heat Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #A6A6A6; border: 2px solid #404040; border-radius: 4px; "></span> Subsurface / Ground Heat Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #FDCF8C; border: 2px solid #404040; border-radius: 4px; "></span> Melt Energy Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

