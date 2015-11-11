#Creates csv file containing download urls and metadata for datasets from USGS 
import arcpy
import datamine_utils
import os

#url variables
api_access_url = 'http://viewer.nationalmap.gov/tnmaccess/api/products'
form_url = 'http://viewer.nationalmap.gov/tnmaccess/api/productsForm'

##global variables
#feature class containing sites
site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'
#output directory for csv file 
csv_output = os.getcwd()
#USGS NED download parameters
dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
product_format = 'IMG'
product_extent = '1 x 1 degree'
date_type = 'dateCreated'
date_start = '' #YYYY-MM-DD
date_end = '' #YYYY-MM-DD 

##get lists of valid url parameters to pass to the GET request (can provide functionality to iterate through each set of parameters, to create multiple csv files)
form_params = datamine_utils.parse_form_params(form_url)
dataset_name_list = form_params['datasets']
product_format_list = form_params['prodFormats']
product_extent_list = form_params['prodExtents']
date_type_list = form_params['dateType']



def main():
	# get site extents
	print "Getting site extents..."
	site_extents = datamine_utils.get_site_extents(site_feature)
	# get all download links
	print "Retrieving all available datasets for your areas of interest..."
	product_table = datamine_utils.generate_product_table(api_access_url,site_extents,dataset,product_format,product_extent,date_type,date_start,date_end)
	print "Total number of datasets to download: ",len(product_table[3])-1 
	#convert to csv
	print "Converting to csv..."
	csv_file = datamine_utils.convert_to_csv(product_table,csv_output)
	print "CSV file saved to: {0}".format(csv_file)
	#open TNM download manager
	print "Opening TNM Download Manager..." 
	datamine_utils.open_download_manager()
	

if __name__ == "__main__":
	main()
