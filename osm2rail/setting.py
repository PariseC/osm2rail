from .web import *
import urllib

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

"""setting for parsing network"""
default_int_buffer = 20.0           # meter
lonlat_precision = 7
xy_precision = 1
default_bounds = {'minlat':-90.0, 'minlon':-180.0, 'maxlat':90.0, 'maxlon':180.0}
railway_poi_set = ['depot','station','workshop','halt','interlocking','junction','spur_junction','terminal','platform']
railway_object=['rail','platform','railway']