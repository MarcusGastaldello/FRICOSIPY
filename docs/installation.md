---
og_title: FRICOSIPY | Installation 
og_description: Guidelines on how to install the FRICOSIPY model
---

# Installation

The *FRICOSIPY* model can be installed by following the proceeding three basic steps:

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Downloading the *FRICOSIPY* Model

**$(1)$**    Download the [latest version](https://github.com/MarcusGastaldello/FRICOSIPY/releases) latest version of the *FRICOSIPY* model from *GitHub* and unpack its contents from the ZIP archive folder.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Changing the Working Directory

**$(2)$**     Navigate to the directory where you have downloaded the *FRICOSIPY* model in the command prompt using the 'cd' (change directory) command: Eg.

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; display:inline-block; max-width:100%; overflow-x:auto; text-align:left;">
  <code style="background:none !important; border:none !important; padding:0 !important; color:#404040; font-family:Consolas, 'Liberation Mono', Courier, monospace;">cd C:\Users\<username>\Downloads\FRICOSIPY</code>
</div>

!!! note

    It is reccomended to move the model to a more suitable working directory.

<hr style="height:2px; background-color:#8b8b8b; border:none;" />

## Creating the *Conda* Environment

**$(3)$**    Create the conda environment using the designated packages in the requirements text file.

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; display:inline-block; max-width:100%; overflow-x:auto; text-align:left;">
  <code style="background:none !important; border:none !important; padding:0 !important; color:#404040; font-family:Consolas, 'Liberation Mono', Courier, monospace;">conda create --name <env> --file requirements.txt</code>
</div>

!!! note

     If you do not have *Miniconda* already installed, you must download and install it first from *Anaconda*: [(https://www.anaconda.com/download)](https://www.anaconda.com/download).

Henceforth, when running the *FRICOSIPY* model you must always ensure this new conda environment is active on your terminal: 

<div style="border:1px solid #ccc; padding:10px; background:#f9f9f9; display:inline-block; max-width:100%; overflow-x:auto; text-align:left;">
  <code style="background:none !important; border:none !important; padding:0 !important; color:#404040; font-family:Consolas, 'Liberation Mono', Courier, monospace;">conda activate <env></code>
</div>

<hr style="height:2px; background-color:#8b8b8b; border:none;" />
