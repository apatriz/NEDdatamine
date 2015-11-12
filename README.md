# NEDdatamine
ArcGIS script tool intended to be used when there is a need to aquire datasets for a large number of specific sites or areas of interest. It takes a polygon feature class containing the areas of interest and finds all USGS datasets available with the given parameters. The parameters are taken directly from The National Map, which ensures they will always be up to date.

# Installation
Requires Python 2.7. This should already be installed with ArcGIS. 
Open the command shell and type:

```
pip install -r /path/to/requirements.txt

```
where /path/to/requirements.txt is the location of the requirements.txt file. This will be in the same directory as the script toolbox.