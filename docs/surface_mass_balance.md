---
og_title: FRICOSIPY | The Surface Mass Balance
og_description: Explanation of the processes and parameterisations used to resolve the Surface Mass Balance (SMB)
---

# Surface Mass Balance



<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; max-width:100%; overflow-x:auto;">
$$
\text{SMB} = \dot{m}_{\text{ precipitation}} + \dot{m}_{\text{ deposition}} + \dot{m}_{\text{ condensation}} - \dot{m}_{\text{ evaporation}} - \dot{m}_{\text{ sublimation}} - \dot{m}_{\text{ surface melt}}
$$
</div>
<small> where . </small>


## Exemplar Surface Mass Balance

The Surface Mass Balance (SMB) illustrates the mass exchange occuring at the surface – either accumulation $(+)$ or ablation $(-)$. In contrast to the energy balance, the monthly mass fluxes do not need to be balanced. **Figure 4** shows an exemplar point surface mass balance for *Colle Gnifetti* at the summit of the *Grenz* glacier, *Valais*, *Switzerland* produced from the *FRICOSIPY* model. For *Colle Gnifetti*, being situated in a high-altitude accumulation area, the net mass exchange is positive.

![Exemplar FRICOSIPY SMB (Surface Mass Balance) Colle Gnifetti](images/Exemplar-SMB.png)

<center><small> **Figure 4**: Exemplar point Surface Mass Balance (SMB) for *Colle Gnifetti* (*Grenz* glacier), *Valais*, *Switzerland* </small></center>

!!! note

    The [*FRICOSIPY result viewer*](result_viewer.md) contains a plotting function that can automatically produce both a surface energy balance and surface mass balance graph (akin to the figures above) for any output dataset.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

<script type="text/javascript">
  document.querySelectorAll('details').forEach(el => {
    el.addEventListener('toggle', () => {
      if (el.open) { MathJax.typesetPromise([el]); }
    });
  });
</script>
