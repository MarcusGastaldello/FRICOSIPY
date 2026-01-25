---
og_title: FRICOSIPY | Result Viewer
og_description: A brief overview of the plotting functions available on the Jupyter Notebook FRICOSIPY result viewer
---

# Result Viewer

The *FRICOSIPY* result viewer is a *Jupyter Notebook* interactive workbook that contains a few plotting functions to help visualise results of the model. It is designed to provide a few examples of how to manipulate Network Common Data Format (NetCDF) files using the *Xarray* python computing package and provide greater accessibility to those less familiar with programming.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Visualising an Xarray Dataset

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Point Surface Energy Balance

A
    
``` python
# Load Python Modules
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Calculate the mean annual energy fluxes:
SHORTWAVE = ds.SHORTWAVE.sel(x = x, y = y).groupby("time.month").mean("time")
SENSIBLE = ds.SENSIBLE.sel(x = x, y = y).groupby("time.month").mean("time")
GROUND = ds.GROUND.sel(x = x, y = y).groupby("time.month").mean("time")
MELT = ds.MELT_ENERGY.sel(x = x, y = y).groupby("time.month").mean("time") * -1
LATENT = ds.LATENT.sel(x = x, y = y).groupby("time.month").mean("time")
LONGWAVE = ds.LONGWAVE.sel(x = x, y = y).groupby("time.month").mean("time")
RAIN_HEAT = ds.RAIN_FLUX.sel(x = x, y = y).groupby("time.month").mean("time")

# Seperate bi-directional energy fluxes:
GROUND_POSITIVE = np.where(GROUND < 0, 0, GROUND)
GROUND_NEGATIVE = np.where(GROUND > 0, 0, GROUND)
LATENT_POSITIVE = np.where(LATENT < 0, 0, LATENT)
LATENT_NEGATIVE = np.where(LATENT > 0, 0, LATENT)
LONGWAVE_POSITIVE = np.where(LONGWAVE < 0, 0, LONGWAVE)
LONGWAVE_NEGATIVE = np.where(LONGWAVE > 0, 0, LONGWAVE)    
    
# Import colourmaps:
Grey = mpl.colormaps['Greys']
RdYlBu = mpl.colormaps['RdYlBu']
Purples = mpl.colormaps['Purples']

# Setup Figure & Axis:
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams.update({'font.size': 9})
fig, ax = plt.subplots(1,1,figsize=(5,5), dpi = 250)
ax.set(ylabel = "Mean Monthly Energy Flux \n [W m$^{-2}$]", xlabel = "Month")
ax.grid(visible=True, which='major', axis='y')

# Bar Chart:
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax.bar(months, SHORTWAVE,         width = 0.8, color = RdYlBu(0.15),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = LONGWAVE_POSITIVE + LATENT_POSITIVE + GROUND_POSITIVE + SENSIBLE, label = "Net Shortwave")
ax.bar(months, SENSIBLE,          width = 0.8, color = RdYlBu(0.25),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = LONGWAVE_POSITIVE + LATENT_POSITIVE + GROUND_POSITIVE, label = "Net Sensible")
ax.bar(months, GROUND_POSITIVE,   width = 0.8, color = Grey(0.5),     alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = LONGWAVE_POSITIVE + LATENT_POSITIVE)
ax.bar(months, LATENT_POSITIVE,   width = 0.8, color = RdYlBu(0.75),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = LONGWAVE_POSITIVE)
ax.bar(months, LONGWAVE_POSITIVE, width = 0.8, color = RdYlBu(0.85),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75)
ax.bar(months, MELT,              width = 0.8, color = RdYlBu(0.35),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, label = "Melt Energy")    
ax.bar(months, GROUND_NEGATIVE,   width = 0.8, color = Grey(0.5),     alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = MELT, label = "Net Ground")
ax.bar(months, LATENT_NEGATIVE,   width = 0.8, color = RdYlBu(0.75),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = MELT + GROUND_NEGATIVE, label = "Net Latent")
ax.bar(months, LONGWAVE_NEGATIVE, width = 0.8, color = RdYlBu(0.85),  alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = MELT + GROUND_NEGATIVE + LATENT_NEGATIVE, label = "Net Longwave")
ax.bar(months, RAIN_HEAT,         width = 0.8, color = Purples(0.50), alpha = 0.85, edgecolor = "gray", linewidth = 0.75, bottom = MELT + GROUND_NEGATIVE + LATENT_NEGATIVE + LONGWAVE_NEGATIVE, label = "Rain Heat")

# Figure Legend:
plt.legend(loc="center right", bbox_to_anchor=(1.4,0.5));
```

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Point Surface Mass Balance

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
