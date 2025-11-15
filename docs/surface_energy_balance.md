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

!!! note

    By convention, 

The *FRICOSIPY* model uses an iterative approach to equalise the energy fluxes; the user can select either a Limited-memory *Broyden*–*Fletcher*–*Goldfarb*–*Shanno* algorithm (L-BFGS) algorithm, the Sequential Least SQuares Programming (SLSQP) approach or the *Newton*-*Raphson* method.

However, since the surface temperature of a glacier is physically constrained to its melting point, excess energy must be apportioned to melt ($Q_{melt}$) should the surface temperature reach 0 $^\circ$C:

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9;">
$$
SW_{net} \pm Q_{sensible} \pm Q_{latent} \pm LW_{net} + Q_{rain} \pm Q_{subsurface} = Q_{melt}
$$
</div>
<div style="height: 20px;"></div>
The following section explains each of these energy fluxes in greater detail and how they are parameterised in the *FRICOSIPY* model.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #E86853; border: 2px solid #404040; border-radius: 4px; "></span>  Shortwave Radiation

Shortwave radiation is the thermal radiation supplied directly from the Sun that ranges from the near ultraviolet (UV), through the visible light (VIS) and to the near infrared (NIR) ranges ($\sim$ 0.2 - 3 $\mu$m) of the electromagnetic spectrum.

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

Longwave radiation (otherwise known as terrestrial radiation) is the thermal radiation emitted between the Earth's surface and atmosphere that is within the infrared classification (3 - 100 $\mu$m) of the electromagnetic spectrum. Net longwave radiation ($LW_{net}$) is calculated in accordance with the *Stefan*–*Boltzmann* law for grey body emission:

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9;">
$$
LW_{net} = LW_{in} - \varepsilon_{s} \: \sigma \: T_{s}^{4}
$$
</div>
<small>where $LW_{net}$  is the net longwave radiation flux, $LW_{in}$ is the incoming longwave radiation, $\varepsilon_{s}$ $\approx$ 0.99 is the surface emissivity, $\sigma$ = 5.67 $\times 10^{-11}$ is the *Stefan*-*Boltzmann* constant and $T_s$ is the surface temperature.</small>

---

### Longwave Radiation Parameterisations 

#### (a) Konzelmann et al. 1994

If the user is unable to provide incoming longwave radiation ($LW_{in}$) in the input meterological data, it can instead by derived from the fractional cloud cover ($N$) using the parametersiations of [Konzelmann et al., 1994](https://doi.org/10.1016/0921-8181(94)90013-2). This substitutes the air temperature ($T_a$) and atmospheric emissivity ($\varepsilon_{atm}$) into the *Stefan*-*Boltzmann* law:


<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #ACA9D0; border: 2px solid #404040; border-radius: 4px; "></span> Rain Heat Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #A6A6A6; border: 2px solid #404040; border-radius: 4px; "></span> Subsurface / Ground Heat Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## <span style="display: inline-block; width: 1em; height: 1em;background-color: #FDCF8C; border: 2px solid #404040; border-radius: 4px; "></span> Melt Energy Flux

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

