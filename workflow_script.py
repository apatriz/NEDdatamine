#Creates csv file containing download urls and metadata for datasets from USGS 
import arcpy
import download_data
import os


#script tool parameters
site_feature = arcpy.GetParameterAsText(0)
dataset = arcpy.GetParameterAsText(1)
product_format = arcpy.GetParameterAsText(2)
product_extent - arcpy.GetParameterAsText(3)


##stand-alone variables
# #feature class containing sites
# site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'

# #USGS NED download parameters
# dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
# product_format = 'IMG'
# product_extent = '1 x 1 degree'

# csv_output = os.getcwd()

product_formats = ["National Boundary Dataset (NBD)","National Elevation Dataset (NED) 1 arc-second",
"Digital Elevation Model (DEM) 1 meter","National Elevation Dataset (NED) 1/3 arc-second","National Elevation Dataset (NED) 1/9 arc-second",
"National Elevation Dataset (NED) Alaska 2 arc-second","Alaska IFSAR 5 meter DEM","National Elevation Dataset (NED) 1/3 arc-second - Contours",
"Original Product Resolution (OPR) Digital Elevation Model (DEM)","Ifsar Digital Surface Model (DSM)"]

def main():
	# get site extents
	print "Getting site extents..."
	site_extents = download_data.get_site_extents(site_feature)
	# get all download links
	print "Searching for available datasets for your areas of interest..."
	product_table = download_data.generate_product_table(site_extents,dataset,product_format,product_extent)
	print "Total number of datasets to download: ",len(product_table[3])-1 
	#convert to csv
	print "Converting to csv..."
	csv_file = download_data.convert_to_csv(product_table,csv_output)
	print "CSV file saved to: {0}".format(csv_file)
	#open TNM download manager
	print "Opening TNM Download Manager..." 
	download_data.open_download_manager()
	

if __name__ == "__main__":
	main()
