---
og_title: FRICOSIPY | The Multi-layer Subsurface Model
og_description: Explanation of the processes and parameterisations governing the evolution of subsurface variables
---

# Multi-layer Subsurface Model

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Precipitation

### Advanced Methods

??? "**$(i)$ Three-Phase Anomaly**"

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Percolation & Refreezing

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Thermal Diffusion

Thermal diffusion is governed by the *Fourier* heat equation:

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
$$
\frac{\delta T}{\delta t} = K \: \frac{\delta^{2} T}{\delta z^{2}} = \frac{k}{\rho \: c_p} \: \frac{\delta^{2} T}{\delta z^{2}}
$$
</div>
<small>where $K$ is the thermal diffusivity $(m^2$ $s^{-1})$, $k$ is the thermal conductivity $(W$ $m^{-1}$ $K^{-1})$, $\rho$ is the density $(kg$ $m^{-3})$ and $c_p$ is the specific heat capacity under constant pressure $(J$ $kg^{-1}$ $K^{-1})$.  </small>
  
In the *FRICOSIPY* model, the heat equation is numerically solved using an explicit, second-order central difference scheme, constrained between two boundary conditions; 
the derived surface temperature $(T_{s})$ from the resolution of the [surface energy balance](https://fricosipy.readthedocs.io/en/latest/surface_energy_balance/) (*Dirichlet*) and a basal / geomethermal heat flux (*Neumann*).

<div markdown="1" style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">

$$
T_i^{\text{ new}} = T_i + \Delta t_{\text{stable}} \left[ \frac{ \frac{K_{i+1/2}\:(T_{i+1} - T_i)}{\Delta z_{i+1/2}} - \frac{K_{i-1/2}\:(T_i - T_{i-1})}{\Delta z_{i-1/2}} }{ \Delta z_i } \right] \qquad (\text{intermediary nodes})
$$

$$
T_n^{\text{ new}} = T_n + \Delta t_{\text{stable}} \left[ \frac{ \frac{Q_{\text{basal}} K_n}{k_n} - \frac{K_{n-1/2} (T_n - T_{n-1})}{\Delta z_{n-1/2}} }{ \frac{1}{4} z_{n-1} + \frac{3}{4} z_n } \right] \qquad (\text{basal node})
$$

</div>

<small>where $i$ is a given subsurface layers, $i \pm 1/2$ , $n$ is the total number of subsurface layers and $\Delta$t is the stable integration timestep. </small>

The stable integration timestap ($\Delta t_{\text{stable}}$) is determined according to the *Von Neumann* stability condition:

<div markdown="1" style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
  
$$
\Delta t_{\text{stable}} \le \frac{1}{2} \min \left( \frac{\Delta z_{i+1/2}^2}{K_{i+1/2}} \right)
$$

</div>

<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Thermal Conductivitiy Parameterisations

??? "**$(i)$ Bulk-volumetric**"

    <br> 
    The bulk-volumetric method is the default approach of the original *COSIPY* model. Thermal conductivity $(k)$ is calculated as a volumetrically-weighted sum of reference values for ice, water and air.
    
    <div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
    $$
    k (\phi) = k_{\:i} \: \phi_{\:i} + k_{\:w} \: \phi_{\:w} + k_{\:a} \: \phi_{\:a}
    $$
    </div>
    <small>where $k_{\:i}$ = 2.22, $k_{\:w}$ = 0.55 & $k_{\:a}$ = 0.024 W m$^{-1}$ are the reference thermal conductivities and $\phi_{\:i}$,$\phi_{\:w}$ & $\phi_{\:a}$ are the volumetric fractions of ice, water and air respectively </small>
    
---

??? "**$(ii)$ Sturm (1997)**"

    <br> 
    Using the parameterisation of [Sturm (1997)](https://doi.org/10.3189/S0022143000002781), thermal conductivity $(k)$ is empirically-derived based on observational data.
    
    <div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
    $$
    k = 
    $$
    </div>
    <small>where </small>

---

??? "**$(iii)$ Calonne et al. (2019)**"

    <br> 
    Using the parameterisation of [Calonne et al. (2019)](https://doi.org/10.1029/2019GL085228), thermal conductivity $(k)$ is empirically-derived based on 3-dimensional image-based computations.
    
    <div markdown="1" style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
    
    $$
    k(\rho,T) = (1-\vartheta) \frac{k_{i}(T) \: k_{\:a}(T)}{k_{\:i}^{\text{ ref}} k_{\:a}^{\text{ ref}}} k_{\text{ snow}}^{\text{ ref}}(\rho) + \vartheta \frac{k_{\:i}(T)}{k_{\:i}^{\text{ ref}}} k_{\text{ firn}}^{\text{ ref}}(\rho)
    $$

    $$
    \vartheta = 1 / \left[ 1 + \text{exp}(-2a \: (\rho - \rho_{\:\text{ transition}})) \right]
    $$
    
    $$
    k_{\text{ firn}}^{\text{ ref}} = 2.107 + 0.003618 \: (\rho - \rho_{i})
    $$
    
    $$
    k_{\text{ snow}}^{\text{ ref}} = 0.024 - 1.23\rho \times 10^{-4} + 2.5 \times 10^{-6}\rho^2
    $$
    
    </div>
    <small>where $k_{\:i}(T)$ and $k_{\:a}(T)$ are the ice and air thermal conductivity at the temperature T, $k_{\:i}^{\text{ ref}}$ = 2.107 and $k_{\:a}^{\text{ ref}}$ = 0.024 <br> W m$^{-1}$ K$^{-1}$ are the ice and air thermal conductivities at the reference temperature of -3 $^\circ$C, $a$ = 0.02 m$^{3}$ kg$^{-1}$ and $\rho_{\:\text{transition}}$ = 450 kg m $^{-3}$. </small>
    
<hr style="height:1px; background-color:#8b8b8b; border:none;" />

### Specific Heat Capacity Parameterisations

??? "**$(i)$ Bulk-volumetric**"

    <br> 
    The bulk-volumetric method is the default approach of the original *COSIPY* model. Specific heat capacity $(c_p)$ is calculated as a volumetrically-weighted sum of reference values for ice, water and air.
    
    <div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
    $$
    c_p (\phi) = c_{\:p,i} \: \phi_{\:i} + c_{\:p,w} \: \phi_{\:w} + c_{\:p,a} \: \phi_{\:a}
    $$
    
    </div>
    <small>where $c_{\:p,i}$ = 2050, $c_{\:p,w}$ = 4217 & $c_{\:p,a}$ = 1004.67 J kg$^{-1}$ K$^{-1}$ are the reference specific heat capacities (for constant pressure) and $\phi_{\:i}$,$\phi_{\:w}$ & $\phi_{\:a}$ are the volumetric fractions of ice, water and air respectively </small>

---

??? "**$(ii)$ Yen (1981)**"

    <br> 
    Using the parameterisation of [Yen (1981)](https://apps.dtic.mil/sti/citations/ADA103734), specific heat capacity $(c_p)$ is empirically-derived based on observational data.
    
    <div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
    $$
    c_p (T) = 152.2 + 7.122 \: T
    $$
    </div>
    
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

