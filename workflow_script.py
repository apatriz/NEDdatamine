# workflow script for processing NED

import arcpy
import os
import list_datasets
import download_data
import re
import csv
import itertools

#feature class containing sites
site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'
#USGS NED download parameters
dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
product_format = 'IMG'
product_extent = '1 x 1 degree'




#get download links
def get_all_links(site_extents,dataset,product_format,product_extent):
	'''(dict,str,str,str) -> list of lists
	
	Takes input dict containing site names and site extents. Dataset,
	product format and product extent parameter strings are set according to
	the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm
	For each site extent entry, a list of dataset product objects is generated (get_link) for datasets that
	cover the site extent. If no products were found, the site name is logged.
	Each download url is checked for duplicates in the final url list 
	("urls[3]"). Next, the product title,fileformat,boundingbox,url,thumbnail, and metadata value are appended to 
	their respective lists, with each list representing a "column" in the data structure. 
	This process repeats for each site extent. 
	Returns the final list of "columns". 
	The output is intended to be converted to a csv and used with the TNM Download Manager for bulk downloading of the datasets.
	
	'''
	
	urls =[['Title'],['FileFormat'],['BoundingBox'],['URL'],['Thumbnail'],['Metadata']]
	missing_datasets = []
	for site_name,site_extent in site_extents.items():
		product_list = download_data.get_products(site_extent,dataset,product_format,product_extent)
		if not product_list:
			missing_datasets.append(site_name)
		else:
			for i in product_list:
				if i['downloadURL'] not in urls[3]:
					urls[0].append(i['title'])
					urls[1].append(i['format'])
					urls[2].append('{0},{1},{2},{3}'.format(i['boundingBox']['minX'],i['boundingBox']['minY'],i['boundingBox']['maxX'],i['boundingBox']['maxY']))
					urls[3].append(i['downloadURL'])
					urls[4].append(i['previewGraphicURL'])
					urls[5].append(i['metaUrl'])
	#TODO: output to logfile instead of print to console
	print "No datasets found for: ",missing_datasets
	return urls

#convert to csv
def convert_to_csv(download_urls):
	''' (list of lists) -> full path string to csv file 
	Takes an input list of lists. 
	Precondition: Each sublist should represent a column of values. The indexes of each sublist should
	correspond to each dataset. i.e. index 0 for each sublist should represent values from the same dataset. 
	Outputs to csv file and returns the output path.
	'''
	with open('all_download_urls.csv','wb') as file:
		wr = csv.writer(file)
		for row in itertools.izip_longest(*download_urls,fillvalue=''):
			wr.writerow(row)
	return os.path.abspath('all_download_urls.csv')
	

# Download the data 
# Manually open the TNM bulk download manager and import the newly created csv file to queue up all the downloads 

def open_download_manager():
	try:
		os.startfile('TNMDownloadManager__V1.2.jar')
	except Exception, e:
		print str(e)

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
	all_links = get_all_links(site_extents,dataset,product_format,product_extent)
	# link_names = []
	# for i in all_links[0]:
		# n = re.findall(r'n[0-9][0-9]w[0-9]{3}',i)
		# print n 
		# # link_names.append(n[0])	
	# print link_names
	print "Total number of datasets to download: ",len(all_links[3])-1 
	# print all_links
	print "Converting to csv..."
	csv_file = convert_to_csv(all_links)
	print "CSV file saved to: {0}".format(csv_file)
	print "Opening TNM Download Manager..." 
	open_download_manager()
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
