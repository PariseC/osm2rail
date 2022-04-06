import urllib
from .web import *

"""setting for Geofabrik downloader (Geofabrik OpenStreetMap data extracts)"""
GeofabrikURL = geofabrik_homepage()
GeofabrikDownloadIndexURL = urllib.parse.urljoin(GeofabrikURL, 'index-v1.json')
GeofabrikValidFileFormats = [".osm.pbf", ".shp.zip", ".osm.bz2"]
GeofabrikDownloadIndexName = 'Geofabrik index of all downloads'
GeofabrikContinentSubregionTableName = 'Geofabrik continent subregions'
GeofabrikRegionSubregionTier = 'Geofabrik region-subregion tier'
GeofabrikDownloadsCatalogue = 'Geofabrik downloads catalogue'
GeofabrikSubregionNameList = 'Geofabrik subregion name list'

"""setting for BBBike downloader (BBBike OpenStreetMap data extracts)"""
BBBikeURL = bbbike_homepage()
BBBikeURLCities = 'https://raw.githubusercontent.com/wosch/bbbike-world/world/etc/cities.txt'
BBBikeCitiesNames = 'BBBike cities'
BBBikeURLCitiesCoordinates = 'https://raw.githubusercontent.com/wosch/bbbike-world/world/etc/cities.csv'
BBBikeCitiesCoordinates = 'BBBike cities coordinates'
BBBikeSubregionCatalogue = 'BBBike subregion catalogue'
BBBikeSubregionNameList = 'BBBike subregion name list'
BBBikeDownloadDictName = 'BBBike download dictionary'


lonlat_precision = 7
default_bounds = {'min_lat':-90.0, 'min_lon':-180.0, 'max_lat':90.0, 'max_lon':180.0}
railway_poi_set = ['depot','station','workshop','halt','interlocking','junction','spur_junction','terminal','platform',
                   'railway']
train_speed_list=[160,200,250,300,350]
block_train_headway={160:6,200:2,250:2,300:2.5,350:3}