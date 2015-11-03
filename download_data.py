import requests
import arcpy
import os
import urllib2
import shutil
from contextlib import closing
import urlparse
import time

##sample url from USGS TNM Access API
##'''http://viewer.nationalmap.gov/tnmaccess/api/products?
##datasets=National+Elevation+Dataset+%28NED%29+1%2F3+arc-second&bbox=-88.117798672%2C38.028972825%2C-88.117608031%2C38.029123082&q=&
##prodFormats=IMG&prodExtents=1+x+1+degree&dateType=dateCreated&start=&end=&polyCode=&polyType=&offset=&max=&outputFormat=JSON'''
site_url = 'http://viewer.nationalmap.gov/tnmaccess/api/products'



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
	
	>>> get_download_link([-97.84059593399996, 39.80099230800005, -97.83959155499997, 39.801785950000045])
	>>> 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/IMG/n40w098.zip'
	>>> get_download_link('-97.84059593399996, 39.80099230800005, -97.83959155499997, 39.801785950000045')
	>>> 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/IMG/n40w098.zip'
  
	'''
##    site_extent = '-88.117798672,38.028972825,-88.117608031,38.029123082'
##    dataset = 'National Elevation Dataset (NED) 1/3 arc-second'
##    product_format = 'IMG'
##    product_extent = '1 x 1 degree'
	products = []
	#set parameters for http request to TNM Access API 
	payload = {'datasets':dataset,'bbox':site_extent,
			   'q':'','prodFormats':product_format,'prodExtents':product_extent,
			   'dateType':'dateCreated','start':'','end':'',
			   'polyCode':'','polyType':'', 'offset':'','max':'','outputFormat':'JSON'}
	
	r = requests.get(site_url,params = payload)
	if r.status_code == requests.codes.ok:
		response = r.json()
		#check if there are results 
		if 'total' in response:
			items = response['items']
			#append each item object to list 
			for i in items:
				products.append(i)
			return products 
		else:
			# print "No datasets found."
			return None
	else:
		r.raise_from_status()
	time.sleep(2)




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
