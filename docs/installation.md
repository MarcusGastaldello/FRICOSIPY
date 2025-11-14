# Installation

The *FRICOSIPY* model can be installed by following the proceeding three steps:

---

**1.**    Download the [latest version](https://github.com/MarcusGastaldello/FRICOSIPY) latest version of the *FRICOSIPY* model from *GitHub* and unpack its contents from the ZIP archive folder.

---

**2.**    Navigate to the directory where you have downloaded the *FRICOSIPY* model in the command prompt using the 'cd' (change directory) command: Eg.

```python
cd C:\Users\<username>\Downloads\FRICOSIPY
```

!!! note

    It is reccomended to move the model to a more suitable working directory.

---

**3.**    Create the conda environment using the designated packages in the requirements text file.

```python
conda create --name <env> --file requirements.txt
```

!!! note

     If you do not have *Miniconda* already installed, you must download and install it first from *Anaconda*: [(https://www.anaconda.com/download)](https://www.anaconda.com/download).

---

Henceforth, when running the *FRICOSIPY* model you must always ensure this new conda environment is active on your terminal: 

```python
conda activate <env>
```
<hr style="height:2px; background-color:#8b8b8b; border:none;" />
