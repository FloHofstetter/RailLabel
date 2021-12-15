<div align="center">
<img src="images/RailLabel.png">
</div>

## Installation
Label tool can be installed in multiple ways.
The preferred way ist to install as python apckage.

### Install as python package (recommended)
You may install this package system-wide, user-wide or in a virtual environment.
0. If necessary, activate the environment
```commandline
source activate <environment name>/bin/activate
```
1. Install the package`rail-label`. User wide installation with the `--user` flag  
```commandline
git+https://github.com/FloHofstetter/labeltool.git
```
Optionally via ssh:
```commandline
pip install git+ssh://git@github.com/FloHofstetter/labeltool.git
```

### Optional: Clone and launch manually
1. Clone this repository
```commandline
https://github.com/FloHofstetter/labeltool.git
git clone 
```
Optionally via ssh:
```commandline
git@github.com:FloHofstetter/labeltool.git
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
