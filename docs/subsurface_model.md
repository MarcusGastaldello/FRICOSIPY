# Multi-layer Subsurface Model



<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Precipitation

### Advanced Methods

??? "**$(i)$ Three-Phase Anomaly**"

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Percolation & Refreezing

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Thermal Diffusion


<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
$$
\frac{\delta T}{\delta t} = K \: \frac{\delta^{2} T}{\delta z^{2}} = \frac{k}{\rho \: c_p} \: \frac{\delta^{2} T}{\delta z^{2}}
$$
</div>
<small>where $K$ is the thermal diffusivity ($m^2$ $s^{-1}$), $k$ is the thermal conductivity ($W$ $m^{-1}$ $K^{-1}$), and specific heat capacity under constant pressure ($J$ $kg^{-1}$ $K^{-1}$)  </small>
  
In the *FRICOSIPY* model, the heat equation is numerically solved using an implicit second-order central difference scheme, constrained between two boundary conditions; 
the derived surface temperature $(T_{s})$ from the resolution of the [surface energy balance](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/) (*Dirichlet*) and a basal / geomethermal heat flux (*Neumann*).


<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Thermal Conductivitiy Parameterisations

??? "**$(i)$ Bulk-volumetric**"

---

??? "**$(ii)$ Sturm (1997)**"

---

??? "**$(iii)$ Calonne et al. (1997)**"

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Specific Heat Capacity Parameterisations

??? "**$(i)$ Bulk-volumetric**"

---

??? "**$(ii)$ Yen (1981)**"

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Dry Firn Densification

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Dry Firn Densification Parameterisations

??? "**$(i)$ Boone (2002)**"

---

??? "**$(ii)$ Ligtenberg et al. (2011)**"

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Snow Metamorphism

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Snow Metamorphism Parameterisations

??? "**$(i)$ Katsushima et al. (2009)**"

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Exemplar Temperature-Depth Profile

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Exemplar Density-Depth Profile

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

