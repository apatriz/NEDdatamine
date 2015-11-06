import requests
import arcpy
import os
import urllib2
import shutil
from contextlib import closing
import urlparse
import time
import csv
import itertools

##sample url from USGS TNM Access API
##'''http://viewer.nationalmap.gov/tnmaccess/api/products?
##datasets=National+Elevation+Dataset+%28NED%29+1%2F3+arc-second&bbox=-88.117798672%2C38.028972825%2C-88.117608031%2C38.029123082&q=&
##prodFormats=IMG&prodExtents=1+x+1+degree&dateType=dateCreated&start=&end=&polyCode=&polyType=&offset=&max=&outputFormat=JSON'''


def get_site_extents(site_feature):
	site_extents = {}
	with arcpy.da.SearchCursor(site_feature,["Name","Shape@"]) as cursor:
		for row in cursor:
			extent = row[1].extent
			site_extents[row[0]] = [extent.XMin,extent.YMin,extent.XMax,extent.YMax]
	return site_extents

#TODO: if no results returned, get another request for different dataset and/or different product formats and product extents
def get_products(site_extent,dataset,product_format,product_extent):
	''' (list/string) -> str
	Takes as input a list of floats representing a spatial extent envelope, in the format [xMin,yMin,xMax,yMax] or as
	a string in the format "xMin,yMin,xMax,yMax". Dataset, product format and product extent parameters are strings. Valid parameters values
	can be obtained from the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm.
	Returns the download link string for the first dataset available in the list
	of returned datasets for the given extent.
	'''
	site_url = 'http://viewer.nationalmap.gov/tnmaccess/api/products'
	#set parameters for http request to TNM Access API 
	payload = {'datasets':dataset,'bbox':site_extent,
			   'q':'','prodFormats':product_format,'prodExtents':product_extent,
			   'dateType':'dateCreated','start':'','end':'',
			   'polyCode':'','polyType':'', 'offset':'','max':'','outputFormat':'JSON'}
	products = []
	r = requests.get(site_url,params = payload)
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
	
	
def generate_product_table(site_extents,dataset,product_format,product_extent):
	'''(dict,str,str,str) -> list of lists
	
	Takes input dict containing site names and site extents. Dataset,
	product format and product extent parameter strings are set according to
	the USGS TNM Access API: http://viewer.nationalmap.gov/tnmaccess/api/productsForm
	For each site extent entry, a list of dataset product objects is generated (get_link) for datasets that
	cover the site extent. If no products were found, the site name is logged.
	Each download url is checked for duplicates in the final url list 
	("urls[3]"). Next, the product title,fileformat,boundingbox,url,thumbnail, and metadata value are appended to 
	their respective sublists, with each sublist representing a "column" in the data structure. 
	Each "row" is a dataset product, and is represented by index number.
	i.e. index 0 ("row 1")of sublist 0 ("column 1") refers to the same dataset product as index 0 ("row 1") of sublist 1 ("column 2").
	This process repeats for each site extent. 
	Returns the final list of lists (i.e. list of "columns"). 
	The output is intended to be converted to a csv and used with the TNM Download Manager for bulk downloading of the datasets.
	
	'''
	
	urls =[['Title'],['FileFormat'],['BoundingBox'],['URL'],['Thumbnail'],['Metadata']]
	missing_datasets = []
	for site_name,site_extent in site_extents.items():
		product_list = get_products(site_extent,dataset,product_format,product_extent)
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
	


def open_download_manager():
	try:
		os.startfile('TNMDownloadManager__V1.2.jar')
	except Exception, e:
		print str(e)



def download_from_link(link,dest):
	filename = os.path.basename(urlparse.urlsplit(link)[2])
	output = os.path.join(dest,filename)
	print "Downloading file: {0} to destination: {1}".format(filename,output)
	with closing(urllib2.urlopen(link)) as r:
		print "Download in progress..."
		with open(output,'wb') as f:
			print "Copying file to destination..."
			shutil.copyfileobj(r,f)
	print "File downloaded successfully to {0}".format(output)
	time.sleep(2)
