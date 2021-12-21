<div align="center">
<img src="images/RailLabel.png">
</div>

## Installation
Label tool can be installed in multiple ways.
The preferred way is to install as python package.


### Install as python package on Windows(recommended)
0. Install Anaconda or Miniconda. Download here: https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html
1. Start Anaconda Prompt
2. Create virtual environment with a python version 3.9:
```commandline
conda create --name <env_name> python=3.9
```
3. Activate virtual environment:
```commandline
conda activate <env_name>
```
4. Install the package`rail-label`. User wide installation with the `--user` flag  
```commandline
pip install git+https://gitlab.rz.htw-berlin.de/se_perception/raillabel.git
```
Optionally via ssh:
```commandline
pip install git+ssh://git@github.com/FloHofstetter/labeltool.git
```


### Install as python package on Linux(recommended)
You may install this package system-wide, user-wide or in a virtual environment.
0. If necessary, create and activate the environment. Minimum python version is 3.9.
```commandline
python3 -m venv venv
```
```commandline
source activate <environment name>/bin/activate
```
1. Install the package`rail-label`. User wide installation with the `--user` flag  
```commandline
pip install git+https://gitlab.rz.htw-berlin.de/se_perception/raillabel.git
```
Optionally via ssh:
```commandline
pip install git@gitlab.rz.htw-berlin.de:se_perception/raillabel.git
```

### Optional: Clone and launch manually
1. Clone this repository
```commandline
git clone https://gitlab.rz.htw-berlin.de/se_perception/raillabel.git
```
Optionally via ssh:
```commandline
git@gitlab.rz.htw-berlin.de:se_perception/raillabel.git
```
2. Create virtual environment and activate
```commandline
python3 -m venv venv
```
3. Install required packages
```commandline
pip install -r requirements.txt
```

## Application
Describe Dataset. images must be in subfolder named 'image'. Do other folders (camera, annotations...) have to be there as well?
Provide path to a dataset on the ML-Server. Make sure, everyone has rights.

1. Change in the dataset directory
```commandline
cd ~/dataset
```
2. Start labeltool
```commandline
python3 -m rail_label
```

Optional start with dataset path as CLI argument:
```commandline
python3 -m rail_label --data_path <dataset path>
```
