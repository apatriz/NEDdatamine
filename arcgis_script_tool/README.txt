# Find USGS Products
ArcGIS script tool intended to be used when there is a need to aquire datasets for a large number of specific sites or areas of interest. 
It takes a polygon feature class containing the areas of interest and finds all USGS datasets available with the given parameters. 
The parameters are taken directly from The National Map, which ensures they will always be up to date.

# Installation
Requires Python 2.7x This should already be installed with ArcGIS. 
Open the command shell and type:


pip install -r /path/to/requirements.txt


where /path/to/requirements.txt is the location of the requirements.txt file. This will be in the same directory as the script toolbox.
You may need to provide the full path to pip (.../Python27/ArcGIS10.2/Scripts/pip.exe): 


/path/to/pip.exe install - r /path/to/requirements.txt


Pip should be installed with Python 2.7.9 and later. If for some reason pip is not installed, you will need to install it manually (which 
may need administrator access).

Download "get-pip.py" (right click, "save link as...") : http://pip.readthedocs.org/en/stable/installing/

Open command shell and type:


python /path/to/get-pip.py


where /path/to/get-pip.py is the location of the downloaded get-pip.py script file.
Note: This assumes that python is correctly added to the PATH system variables on your machine. If not, you will have to supply the full
path to the python executable. 


/path/to/python.exe /path/to/get-pip.py


