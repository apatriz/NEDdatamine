# workflow script for processing NED

import arcpy
import os
import list_datasets
import download_data

#feature class containing sites
site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'
#USGS NED download parameters
dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
product_format = 'IMG'
product_extent = '1 x 1 degree'




#get download links
def get_all_links(site_extents):
	urls =[]
	missing_datasets = []
	get_link = download_data.get_download_link
	for site_name,site_extent in site_extents.items():
		url = get_link(site_extent,dataset,product_format,product_extent)
		if not url:
			missing_datasets.append(site_name)
		elif url not in urls:
			urls.append(url)				
	#TODO: output to logfile instead of print to console
	print "No datasets found for: ",missing_datasets
	return urls


#download datasets

# project to Albers

# Run slope (degrees)

#create zone raster from site polygons (use name field)

# Run MEAN zonal statistics as table using zone raster (name field)

# Join output table to site polygons and create new field 'Slope_Avg' to store the values

#Run aspect, use Copy Raster to save as 16-bit signed (for Majority stats.)

# Run MAJORITY zonal stats. as table on aspect raster

#Join table to site polygons and create new field 'Aspect' to save table values

def main():
	# get site extents
	print "Getting site extents..."
	site_extents = download_data.get_site_extents(site_feature)
	# print len(site_extents)
	# get all download links
	print "Getting NED dataset urls..."
	all_links = get_all_links(site_extents)
	print "Total number of links: ",len(all_links)
	print all_links

	
	

if __name__ == "__main__":
	main()
