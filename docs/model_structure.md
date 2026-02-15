---
og_title: FRICOSIPY | Model Structure
og_description: A schematic diagram showing the model structure of FRICOSIPY
---

# Model Structure

The following interactive diagram shows the structure of the *FRICOSIPY*, allowing new users to familiarise themselves with the model. Unless the user intents to adapt the model, it is only necessary to interact with the main *Python* scipts in the root directory to run a *FRICOSIPY* simulation.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

??? "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **main**"
    <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">The main model directory containing all core computational scripts.</div>

    ???+ "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **kernel**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Core calculation and infrastructure scripts.</div>

        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">fricosipy_core.py</h4><div>The central logic engine for the model.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">io.py</h4><div>Input/Output handling for data files.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">grid.py</h4><div>Spatial grid definitions and management.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">node.py</h4><div>Node-level calculation functions.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">init.py</h4><div>Initialization scripts for simulation startup.</div></div></div>

    ???+ "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **modules**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Individual physical parameterizations.</div>

        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">shortwave_radiation.py</h4><div>Calculates solar energy inputs.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">albedo.py</h4><div>Surface reflectance modeling.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">penetrating_radiation.py</h4><div>Subsurface radiation absorption.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">surface_roughness.py</h4><div>Aerodynamic roughness calculations.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">surface_temperature.py</h4><div>Energy balance for surface skin temperature.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">darcy_fluxes.py</h4><div>Water movement through the snow/ice pack.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">percolation_refreezing.py</h4><div>Meltwater dynamics and latent heat release.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">thermal_diffusion.py</h4><div>Heat conduction through layers.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">snow_metamorphism.py</h4><div>Evolution of snow grain size and properties.</div></div></div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">densification.py</h4><div>Compaction and firn-to-ice transition logic.</div></div></div>

??? "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **data**"
    <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">The data directory containing all the model input and output files.</div>

    ???+ "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **static**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Topographic information that varies across the spatial domain $(x,y)$.</div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">static.nc</h4><div>An exemplar input static NetCDF file.</div></div></div>

    ??? "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **meteo**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Meteorological time-series data.</div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">meteo.nc</h4><div>An exemplar input meteo NetCDF file that contains meteorological data varying through time $(t)$.</div></div></div>

    ??? "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **illumination**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Solar illumination mapping for grid nodes.</div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">illumination.nc</h4><div>An exemplar input illumination NetCDF file for given timesteps $(t)$.</div></div></div>

    ??? "<img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='vertical-align:middle; margin-right:15px;'> **output**"
        <div style="padding-left: 115px; margin-top: -30px; margin-bottom: 20px;">Results and log files.</div>
        <div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h4 style="margin:0;">output.nc</h4><div>The resulting file containing the FRICOSIPY simulation data.</div></div></div>

<div style="display:flex; align-items:center; margin:30px 0 25px 0;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">docs</h2><div>Documentation scripts for the Read the Docs website.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">FRICOSIPY.py</h2><div>The main executable file of the FRICOSIPY model.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">config.py</h2><div>Configuration setup for current simulations.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">parameters.py</h2><div>The parameters file that allows the user to specify the parameterisations and set the parameter values used in the simulation.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">constants.py</h2><div>Fixed physical constants used in model calculations.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Jupyter.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">result_viewer.ipynb</h2><div>Notebook for results visualization.</div></div></div>

<div style="display:flex; align-items:center; margin-bottom:25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Text.png" width="100" style="margin-right:15px;"><div style="flex:1;"><h2 style="margin:0;">requirements.txt</h2><div>Python package requirements list.</div></div></div>

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
