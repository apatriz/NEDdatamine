# workflow script for processing NED

import arcpy
import os
import list_datasets
import download_data
import re
import csv

#feature class containing sites
site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'
#USGS NED download parameters
dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
product_format = 'IMG'
product_extent = '1 x 1 degree'




#get download links
def get_all_links(site_extents,dataset,product_format,product_extent):
	'''(dict,str,str,str) -> list
	
	Takes input dict containing site names and site extents. Dataset,
	product format and product extent parameter strings are set according to
	the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm
	For each site extent entry, a list of download urls is generated (get_link) for datasets that
	cover the site extent. Each download url is checked for duplicates against the final list 
	("urls"). This process iterates over each site extent. 
	Returns the final list of unique download urls.
	
	'''
	
	urls =[['URL'],[]]
	missing_datasets = []
	get_link = download_data.get_download_link
	for site_name,site_extent in site_extents.items():
		link_list = get_link(site_extent,dataset,product_format,product_extent)
		if not link_list:
			missing_datasets.append(site_name)
		else:
			for i in link_list:
				if i not in urls[1]:
					urls[1].append(i)
	#TODO: output to logfile instead of print to console
	print "No datasets found for: ",missing_datasets
	return urls

#convert to csv
#TODO: fix links data structure ---writing them to single row
def convert_to_csv(download_urls):
	with open('all_download_urls.csv','wb') as file:
		wr = csv.writer(file)
		wr.writerows(download_urls)
	
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
	all_links = get_all_links(site_extents,dataset,product_format,product_extent)
	# link_names = []
	# for i in all_links:
		# n = re.findall(r'n[0-9][0-9]w[0-9]{3}',i)
		# link_names.append(n[0])	
	# print len(link_names),link_names
	print "Total number of download links: ",len(all_links[1])
	print all_links
	print "Converting to csv..."
	convert_to_csv(all_links)
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
