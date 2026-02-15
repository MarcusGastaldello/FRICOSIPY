---
og_title: FRICOSIPY | Model Structure
og_description: A schematic diagram showing the model structure of FRICOSIPY
---

# Model Structure

The following interactive diagram shows the structure of the *FRICOSIPY*, allowing new users to familiarise themselves with the model. Unless the user intends to adapt the model, it is only necessary to interact with the main *Python* scripts in the root directory to run a *FRICOSIPY* simulation.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

??? "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100'></td><td style='padding-left:15px; vertical-align:middle;'><h2 style='margin:0;'>main</h2><small style='color:gray;'>The main model directory containing all core computational scripts.</small></td></tr></table>"

    ???+ "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>kernel</h3><small style='color:gray;'>Core calculation and infrastructure scripts.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">fricosipy_core.py</h4><small style="color:gray;">The central logic engine for the model.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">io.py</h4><small style="color:gray;">Input/Output handling for data files.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">grid.py</h4><small style="color:gray;">Spatial grid definitions and management.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">node.py</h4><small style="color:gray;">Node-level calculation functions.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">init.py</h4><small style="color:gray;">Initialization scripts for simulation startup.</small></div></div>

    ???+ "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>modules</h3><small style='color:gray;'>Individual physical parameterizations.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">shortwave_radiation.py</h4><small style="color:gray;">Calculates solar energy inputs.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">albedo.py</h4><small style="color:gray;">Surface reflectance modeling.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">penetrating_radiation.py</h4><small style="color:gray;">Subsurface radiation absorption.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">surface_roughness.py</h4><small style="color:gray;">Aerodynamic roughness calculations.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">surface_temperature.py</h4><small style="color:gray;">Energy balance for surface skin temperature.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">darcy_fluxes.py</h4><small style="color:gray;">Water movement through the snow/ice pack.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">percolation_refreezing.py</h4><small style="color:gray;">Meltwater dynamics and latent heat release.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">thermal_diffusion.py</h4><small style="color:gray;">Heat conduction through layers.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">snow_metamorphism.py</h4><small style="color:gray;">Evolution of snow grain size and properties.</small></div></div>
        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">densification.py</h4><small style="color:gray;">Compaction and firn-to-ice transition logic.</small></div></div>

??? "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100'></td><td style='padding-left:15px; vertical-align:middle;'><h2 style='margin:0;'>data</h2><small style='color:gray;'>The data directory containing all the model input and output files.</small></td></tr></table>"

    ???+ "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>static</h3><small style='color:gray;'>Topographic information that varies across the spatial domain $(x,y)$.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">static.nc</h4><small style="color:gray;">An exemplar input static NetCDF file.</small></div></div>

    ??? "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>meteo</h3><small style='color:gray;'>Meteorological time-series data.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">meteo.nc</h4><small style="color:gray;">Meteorological data varying through time $(t)$.</small></div></div>

    ??? "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>illumination</h3><small style='color:gray;'>Solar illumination mapping for grid nodes.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">illumination.nc</h4><small style="color:gray;">Input illumination file for leap and standard years.</small></div></div>

    ??? "<table style='border:none; border-collapse:collapse; margin-left:-25px;'><tr><td style='padding:0; vertical-align:middle;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='80'></td><td style='padding-left:15px; vertical-align:middle;'><h3 style='margin:0;'>output</h3><small style='color:gray;'>Results and log files.</small></td></tr></table>"

        <div style="margin-bottom:20px; display:flex; align-items:center;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="80" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">output.nc</h4><small style="color:gray;">The resulting file containing the FRICOSIPY simulation data.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">docs</h2><small style="color:gray;">Documentation scripts for the Read the Docs website.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">FRICOSIPY.py</h2><small style="color:gray;">The main executable file of the FRICOSIPY model.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex: 1;"><h2 style="margin: 0;">config.py</h2><small style="color: gray;">Configuration setup for current simulations.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">parameters.py</h2><small style="color:gray;">Specification of parameterizations and values.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">constants.py</h2><small style="color:gray;">Fixed physical constants used in model calculations.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Jupyter.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">result_viewer.ipynb</h2><small style="color:gray;">Notebook for results visualization.</small></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Text.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">requirements.txt</h2><small style="color:gray;">Python package requirements list.</small></div></div>

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
