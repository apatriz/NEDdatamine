# workflow script for processing NED

import list_datasets
import download_data
import re

#feature class containing sites
site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'
#USGS NED download parameters
dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
product_format = 'IMG'
product_extent = '1 x 1 degree'




#get download links

# Download the data 
# open the TNM bulk download manager and import the newly created csv file to queue up all the downloads 

# Mosiac all datasets

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
	print "Retrieving all available datasets..."
	product_table = download_data.generate_product_table(site_extents,dataset,product_format,product_extent)
	# link_names = []
	# for i in product_table[0]:
		# n = re.findall(r'n[0-9][0-9]w[0-9]{3}',i)
		# print n 
		# # link_names.append(n[0])	
	# print link_names
	print "Total number of datasets to download: ",len(product_table[3])-1 
	# print product_table
	print "Converting to csv..."
	csv_file = download_data.convert_to_csv(product_table)
	print "CSV file saved to: {0}".format(csv_file)
	print "Opening TNM Download Manager..." 
	download_data.open_download_manager()
	# already_downloaded = list_datasets.list_datasets('C:\\Fakhoury_DataMining\\NED_10m\\raw_data',datatype='RasterDataset',type='IMG')
	# name_list = []
	# for i in already_downloaded:
		# n = re.findall(r'n[0-9][0-9]w[0-9]{3}',i)
		# name_list.append(n[0])	
	# for e in name_list:
		# if e not in link_names:
			# print e 

	

if __name__ == "__main__":
	main()
