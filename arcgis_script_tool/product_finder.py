# For use as ArcGIS script tool. Outputs a csv file containing links and metadata for retreived USGS datasets. Can be imported 
# into TNM Download manager to bulk download the datasets.

import arcpy
import os
import time
import csv
import itertools
import requests
import bs4
from datetime import datetime


#url variables
api_access_url = 'http://viewer.nationalmap.gov/tnmaccess/api/products'
form_url = 'http://viewer.nationalmap.gov/tnmaccess/api/productsForm'

#arcpy parameters
site_feature = arcpy.GetParameterAsText(0)
csv_output = arcpy.GetParameterAsText(1)
dataset = arcpy.GetParameterAsText(2) or ''
product_format = arcpy.GetParameterAsText(3) or ''
product_extent = arcpy.GetParameterAsText(4) or ''
# TODO: implement calendar widget for date inputs
date_type = arcpy.GetParameterAsText(5) or 'dateCreated'
date_start = arcpy.GetParameterAsText(6) or ''
date_end = arcpy.GetParameterAsText(7) or ''
#change date parameters to correct format
if date_start:
	if len(date_start) > 10:
		date_start = date_start[:date_start.find(' ')]
	changed_date_start = datetime.strptime(date_start,"%m/%d/%Y")
	date_start = datetime.strftime(changed_date_start, "%Y-%m-%d")
if date_end:
	if len(date_end) > 10:
		date_end = date_end[:date_end.find(' ')]
	changed_date_end = datetime.strptime(date_end,"%m/%d/%Y")
	date_end = datetime.strftime(changed_date_end, "%Y-%m-%d")

arcpy.AddMessage("AOI Feature Class: {0}\nOutput Location: {1}\nDataset: {2}\nProduct Format: {3}\n"
	"Product Extent: {4}\nDate Type: {5}\nDate Start: {6}\nDate End: {7}\n".format(site_feature,csv_output,dataset,product_format,product_extent,date_type,date_start,date_end))

### This function is used in Script Tool validation code to update parameter lists when opening the tool  
# def parse_form_params(site_to_parse):
	# '''
	# Gets html response using requests lib. Parses content and retrieves all  <select> tags and <option> values using BeautifulSoup. 
	# Returns a dict with <select> tag 'name' attribute as the key, and a list of it's child <option> tag 'value' attributes as value.
	
	# >>> parse_form_params('http://viewer.nationalmap.gov/tnmaccess/api/productsForm')
	# >>> {'datasets':['NED 1/3 arcsecond','NED 1/9 arcsecond'],'prodFormats':['IMG','BIL','GRID']}
	
	# '''
	# res = requests.get(site_to_parse)
	# html = res.content
	# soup = bs4.BeautifulSoup(html,'lxml')
	# form_params = {}
	# select_tags = soup.find_all('select')
	# for tag in select_tags:
		# name = tag['name']
		# option_values = [option.get('value') for option in tag.find_all('option') if option.get('value')]
		# form_params[name] = option_values
	# return form_params

### get lists of valid url parameters to pass to the GET request (can provide future functionality to iterate through each set of parameters, to create multiple csv files)	
# # form_params = parse_form_params(form_url)
# # dataset_name_list = form_params['datasets']
# # product_format_list = form_params['prodFormats']
# # product_extent_list = form_params['prodExtents']
# # date_type_list = form_params['dateType']




def get_site_extents(site_feature):
	site_extents = {}
	with arcpy.da.SearchCursor(site_feature,["Name","Shape@"]) as cursor:
		for row in cursor:
			extent = row[1].extent
			site_extents[row[0]] = [extent.XMin,extent.YMin,extent.XMax,extent.YMax]
	return site_extents
	

#TODO: if no results returned, get another request for different dataset and/or different product formats and product extents
def get_products(access_url,site_extent,dataset,product_format,product_extent,date_type,date_start,date_end):
	''' (list/string) -> str
	Takes as input a list of floats representing a spatial extent envelope, in the format [xMin,yMin,xMax,yMax] or as
	a string in the format "xMin,yMin,xMax,yMax". Dataset, product format and product extent parameters are strings. Valid parameters values
	can be obtained from the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm.
	Returns the download link string for the first dataset available in the list
	of returned datasets for the given extent.
	'''
	#set parameters for http request to TNM Access API 
	payload = {'datasets':dataset,'bbox':site_extent,
			   'q':'','prodFormats':product_format,'prodExtents':product_extent,
			   'dateType':date_type,'start':date_start,'end':date_end,
			   'polyCode':'','polyType':'', 'offset':'','max':'','outputFormat':'JSON'}
	products = []
	r = requests.get(access_url,params = payload)
	if r.status_code == requests.codes.ok:
		response = r.json()
		#check if there are results 
		if 'total' in response:
			items = response['items']
			#append each item object to products list 
			for i in items:
				products.append(i)
			return products 
		else:
			# print "No datasets found."
			return None
	else:
		r.raise_from_status()
	time.sleep(2)
	
	
def generate_product_table(access_url,site_extents,dataset,product_format,product_extent,date_type,date_start,date_end):
	'''(dict,str,str,str) -> list of lists
	
	Takes input dict containing site names and site extents. Dataset,
	product format and product extent parameter strings are set according to
	the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm
	For each site extent entry, a list of dataset product objects is generated (get_link) for datasets that
	cover the site extent. If no products were found, the site name is logged.
	Each download url is checked for duplicates in the final url list 
	("columns[3]"). Next, the product title,fileformat,boundingbox,url,thumbnail, and metadata value are appended to 
	their respective sublists, with each sublist representing a "column" in the data structure. 
	Each "row" is a dataset product, and is represented by index number.
	i.e. index 0 ("row 1")of sublist 0 ("column 1") refers to the same dataset product as index 0 ("row 1") of sublist 1 ("column 2").
	This process repeats for each site extent. 
	Returns the final list of lists (i.e. list of "columns"). 
	The output is intended to be converted to a csv and used with the TNM Download Manager for bulk downloading of the datasets.
	
	'''	
	columns =[['Title'],['FileFormat'],['BoundingBox'],['URL'],['Thumbnail'],['Metadata']]
	missing_datasets = []
	for site_name,site_extent in site_extents.items():
		product_list = get_products(access_url,site_extent,dataset,product_format,product_extent,date_type,date_start,date_end)
		if not product_list:
			missing_datasets.append(site_name)
		else:
			for i in product_list:
				if i['downloadURL'] not in columns[3]:
					columns[0].append(i['title'])
					columns[1].append(i['format'])
					columns[2].append('{0},{1},{2},{3}'.format(i['boundingBox']['minX'],i['boundingBox']['minY'],i['boundingBox']['maxX'],i['boundingBox']['maxY']))
					columns[3].append(i['downloadURL'])
					columns[4].append(i['previewGraphicURL'])
					columns[5].append(i['metaUrl'])
	#TODO: output to logfile instead of print to console
	if missing_datasets:
		arcpy.AddWarning("No datasets found for {0} sites: {1}".format(len(missing_datasets),missing_datasets))
	return columns


def convert_to_csv(download_urls,output_dir):
	''' (list of lists) -> full path string to csv file 
	Takes an input list of lists. 
	Precondition: Each sublist should represent a column of values. The indexes of each sublist should
	correspond to each dataset. i.e. index 0 for each sublist should represent values from the same dataset. 
	Outputs to csv file and returns the output path.
	'''
	file_name = 'download_links.csv'
	output = os.path.join(output_dir,file_name)
	with open(output,'wb') as file:
		wr = csv.writer(file)
		for row in itertools.izip_longest(*download_urls,fillvalue=''):
			wr.writerow(row)
	return output
	


def open_download_manager():
	script_dir = os.path.dirname(os.path.realpath(__file__))
	os.startfile(os.path.join(script_dir,'TNMDownloadManager__V1.2.jar'))
	time.sleep(2)
	



def main():
	# get site extents
	arcpy.AddMessage("Getting site extents...")
	site_extents = get_site_extents(site_feature)
	# get all download links
	arcpy.AddMessage("Retrieving all available datasets for your areas of interest...")
	product_table = generate_product_table(api_access_url,site_extents,dataset,product_format,product_extent,date_type,date_start,date_end)
	if len(product_table[3])-1 != 0:
		arcpy.AddMessage("Total number of datasets to download: {0}".format(len(product_table[3])-1)) 
	else:
		arcpy.AddWarning("No datasets found. Change your search parameters and run the tool again.")
		raise sys.exit()
	#convert to csv
	arcpy.AddMessage("Converting to csv...")
	csv_file = convert_to_csv(product_table,csv_output)
	arcpy.AddMessage("CSV file saved to: {0}".format(csv_file)) 
	#open TNM download manager
	try:
		arcpy.AddMessage("Attempting to open TNM Download Manager...")
		open_download_manager()
		arcpy.AddMessage("Import {0} into TNM Download Manager to start bulk download.".format(csv_file))
	except Exception, e:
		arcpy.AddWarning(str(e))
		arcpy.AddWarning("Ensure TNM Download Manager is located in the same directory as 'product_finder.py'.")
	
		

if __name__ == "__main__":
	main()
