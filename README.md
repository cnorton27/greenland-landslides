# greenland-landslides
GitHub repo for analysis of landslide hazards in Greenland


## Setting up environment

If using conda env. (recommended when using geospatial packages that have C++ binaries) run these lines in your terminal to 
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict

Create env by running: 
conda env create -f environment.yml

or if using .venv run:

pip install -r requirements.txt

**gdal often doesn't compile properly when installed in a .venv

if you already have a conda env run:

conda install --file requirements.txt

