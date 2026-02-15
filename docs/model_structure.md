---
og_title: FRICOSIPY | Model Structure
og_description: A schematic diagram showing the model structure of FRICOSIPY
---

# Model Structure

The following interactive diagram shows the structure of the *FRICOSIPY*, allowing new users to familiarise themselves with the model. Unless the user intents to adapt the model, it is only necessary to interact with the main *Python* scipts in the root directory to run a *FRICOSIPY* simulation.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h2 style='margin: 0;'>main</h2><small style='display: block; color: gray; margin-top: 4px;'>The main model directory containing all core computational scripts.</small></div></div>"

    <div style="margin-top: 20px; margin-left: 10px;">
    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>kernel</h3><small style='display: block; color: gray; margin-top: 4px;'>Core calculation and infrastructure scripts.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">fricosipy_core.py</h4><small style="color: gray; display: block; margin-top: 4px;">The central logic engine for the model.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">io.py</h4><small style="color: gray; display: block; margin-top: 4px;">Input/Output handling for data files.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">grid.py</h4><small style="color: gray; display: block; margin-top: 4px;">Spatial grid definitions and management.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">node.py</h4><small style="color: gray; display: block; margin-top: 4px;">Node-level calculation functions.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">init.py</h4><small style="color: gray; display: block; margin-top: 4px;">Initialization scripts for simulation startup.</small></div></div>
        </div>

    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>modules</h3><small style='display: block; color: gray; margin-top: 4px;'>Individual physical parameterizations.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">shortwave_radiation.py</h4><small style="color: gray; display: block; margin-top: 4px;">Calculates solar energy inputs.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">albedo.py</h4><small style="color: gray; display: block; margin-top: 4px;">Surface reflectance modeling.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">penetrating_radiation.py</h4><small style="color: gray; display: block; margin-top: 4px;">Subsurface radiation absorption.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">surface_roughness.py</h4><small style="color: gray; display: block; margin-top: 4px;">Aerodynamic roughness calculations.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">surface_temperature.py</h4><small style="color: gray; display: block; margin-top: 4px;">Energy balance for surface skin temperature.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">darcy_fluxes.py</h4><small style="color: gray; display: block; margin-top: 4px;">Water movement through the snow/ice pack.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">percolation_refreezing.py</h4><small style="color: gray; display: block; margin-top: 4px;">Meltwater dynamics and latent heat release.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">thermal_diffusion.py</h4><small style="color: gray; display: block; margin-top: 4px;">Heat conduction through layers.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">snow_metamorphism.py</h4><small style="color: gray; display: block; margin-top: 4px;">Evolution of snow grain size and properties.</small></div></div>
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">densification.py</h4><small style="color: gray; display: block; margin-top: 4px;">Compaction and firn-to-ice transition logic.</small></div></div>
        </div>
    </div>

??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h2 style='margin: 0;'>data</h2><small style='display: block; color: gray; margin-top: 4px;'>The data directory containing all the model input and output files.</small></div></div>"

    <div style="margin-top: 20px; margin-left: 10px;">
    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>static</h3><small style='display: block; color: gray; margin-top: 4px;'>Topographic information that varies across the spatial domain $(x,y)$.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">static.nc</h4><small style="color: gray; display: block; margin-top: 4px;">An exemplar input static NetCDF file.</small></div></div>
        </div>

    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>meteo</h3><small style='display: block; color: gray; margin-top: 4px;'>Meteorological time-series data.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">meteo.nc</h4><small style="color: gray; display: block; margin-top: 4px;">An exemplar input meteo NetCDF file that contains meteorological data varying through time $(t)$.</small></div></div>
        </div>

    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>illumination</h3><small style='display: block; color: gray; margin-top: 4px;'>Solar illumination mapping for grid nodes.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">illumination.nc</h4><small style="color: gray; display: block; margin-top: 4px;">An exemplar input illumination NetCDF file for given timesteps $(t)$.</small></div></div>
        </div>

    ??? "<div style='display: flex; align-items: center; margin-left: -25px;'><img src='https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png' width='100' style='margin-right: 15px; flex-shrink: 0;'><div style='flex: 1;'><h3 style='margin: 0;'>output</h3><small style='display: block; color: gray; margin-top: 4px;'>Results and log files.</small></div></div>"

        <div style="padding-top: 20px; margin-left: 10px;">
        <div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/NetCDF.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h4 style="margin: 0;">output.nc</h4><small style="color: gray; display: block; margin-top: 4px;">The resulting file containing the FRICOSIPY simulation data.</small></div></div>
        </div>
    </div>

<div style="display: flex; align-items: center; margin: 30px 0 25px 0;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Folder.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">docs</h2><small style="color: gray; display: block; margin-top: 4px;">Documentation scripts for the Read the Docs website.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">FRICOSIPY.py</h2><small style="color: gray; display: block; margin-top: 4px;">The main executable file of the FRICOSIPY model.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">config.py</h2><small style="color: gray; display: block; margin-top: 4px;">Configuration setup for current simulations.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">parameters.py</h2><small style="color: gray; display: block; margin-top: 4px;">Specification of parameterizations and values.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Python.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">constants.py</h2><small style="color: gray; display: block; margin-top: 4px;">Fixed physical constants used in model calculations.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Jupyter.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">result_viewer.ipynb</h2><small style="color: gray; display: block; margin-top: 4px;">Notebook for results visualization.</small></div></div>

<div style="display: flex; align-items: center; margin-bottom: 25px;"><img src="https://github.com/MarcusGastaldello/FRICOSIPY/raw/main/docs/icons/Text.png" width="100" style="margin-right: 15px; flex-shrink: 0;"><div style="flex: 1;"><h2 style="margin: 0;">requirements.txt</h2><small style="color: gray; display: block; margin-top: 4px;">Python package requirements list.</small></div></div>

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
