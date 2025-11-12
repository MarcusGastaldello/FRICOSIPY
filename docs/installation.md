# Installation

**1.**    Download the latest version of the FRICOSIPY model and unpack its contents from the ZIP archive folder.

**2.**    Navigate to the directory where you have downloaded the FRICOSIPY model in the command prompt using the 'cd' (change directory) command: Eg.

```python
cd C:\Users\<username>\Downloads\FRICOSIPY
```

!!!

    It is reccomended to move the model to a more suitable directory.

**3.**    Create the conda environment. If you do not have *Miniconda* already installed, you must install it first (https://www.anaconda.com/download).

```python
conda create --name <env> --file requirements.txt
```

Henceforth, when running the FRICOSIPY model you must always ensure this new conda environment is active: 

```python
conda activate <env>
```
