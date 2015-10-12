import requests
import arcpy
import os
import urllib2
import shutil
from contextlib import closing
import urlparse
import time

##r = requests.get('http://viewer.nationalmap.gov/tnmaccess/api/products')
##'''http://viewer.nationalmap.gov/tnmaccess/api/products?
##datasets=National+Elevation+Dataset+%28NED%29+1%2F3+arc-second&bbox=-88.117798672%2C38.028972825%2C-88.117608031%2C38.029123082&q=&
##prodFormats=IMG&prodExtents=1+x+1+degree&dateType=dateCreated&start=&end=&polyCode=&polyType=&offset=&max=&outputFormat=JSON'''


site_feature = 'C:/Fakhoury_DataMining/Fakhoury.gdb/Fakhoury_Polygons'

def get_site_extents(site_feature):
    site_extents = []
    with arcpy.da.SearchCursor(site_feature,"Shape@") as cursor:
        for row in cursor:
            extent = row[0].extent
            site_extents.append([extent.XMin,extent.YMin,extent.XMax,extent.YMax])
    return site_extents

#TODO: if no results returned, post another request for different dataset and/or different product formats and product extents
def get_download_link(site_extent):
    ''' (list/string) -> str

    Takes as input a list of floats representing a spatial extent envelope, in the format [xMin,yMin,xMax,yMax] or as
    a string in the format "xMin,yMin,xMax,yMax".
    Returns the download link string for the first dataset available in the list
    of returned datasets for the given extent.
    
    >>> get_download_link([-97.84059593399996, 39.80099230800005, -97.83959155499997, 39.801785950000045])
    >>> 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/IMG/n40w098.zip'
    >>> get_download_link('-97.84059593399996, 39.80099230800005, -97.83959155499997, 39.801785950000045')
    >>> 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/NED/13/IMG/n40w098.zip'
  
    '''
##    site_extent = '-88.117798672,38.028972825,-88.117608031,38.029123082'
    payload = {'datasets':'National Elevation Dataset (NED) 1/3 arc-second','bbox':site_extent,
               'q':'','prodFormats':'IMG','prodExtents':'1 x 1 degree',
               'dateType':'dateCreated','start':'','end':'',
               'polyCode':'','polyType':'', 'offset':'','max':'','outputFormat':'JSON'}
    r = requests.get('http://viewer.nationalmap.gov/tnmaccess/api/products',params = payload)
    if r.status_code == requests.codes.ok:
        response = r.json()
        if response['total']:
            return str(response['items'][0]['downloadURL'])
        else:
            return "No datasets found."
    else:
        r.raise_from_status()
    time.sleep(1)




def download_from_link(link,dest):
    filename = os.path.basename(urlparse.urlsplit(link)[2])
    print filename
    output = os.path.join(dest,filename)
    print output
    print "Downloading..."
    with closing(urllib2.urlopen(link)) as r:
        with open(output,'wb') as f:
            shutil.copyfileobj(r,f)
    print "File downloaded successfully to {0}".format(output)
    time.sleep(1)
    
    
