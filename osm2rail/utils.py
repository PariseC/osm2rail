import fake_useragent
import random
import os
import math
import pickle
import pathlib
import pkg_resources
from pyhelpers.dir import cd


def validate_download_dir(download_dir):
    if download_dir:
        if not os.path.isabs(download_dir):
            download_dir=download_dir.strip('.\\.')
            current_filepath = os.getcwd()
            download_dir = os.path.join(current_filepath, download_dir)
    else:
        current_filepath = os.getcwd()
        download_dir=os.path.join(current_filepath,'osmfile')

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    return download_dir

def cd_dat(*sub_dir, dat_dir="dat", mkdir=False, **kwargs):
    path = pkg_resources.resource_filename(__name__, dat_dir)

    for x in sub_dir:
        path = os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)

        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path

def cd_dat_geofabrik(*sub_dir, mkdir=False, **kwargs):

    path = cd("dat_Geofabrik", *sub_dir, mkdir=mkdir, **kwargs)

    return path

def cd_dat_bbbike(*sub_dir, mkdir=False, **kwargs):

    path = cd("dat_BBBike", *sub_dir, mkdir=mkdir, **kwargs)

    return path


"""                                 """
def get_distance_from_coord(lon1, lat1, lon2, lat2):
    # return km
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def prase_link_geometry(link_geometry_str):
    geometry=link_geometry_str.replace('LINESTRING','')
    geometry=geometry.replace('(','')
    geometry = geometry.replace(')', '')
    geometry = geometry.split(',')
    x_coord=[]
    y_coord=[]
    for id in range(len(geometry)):
        coord_str=geometry[id].lstrip()
        coord_str=coord_str.split(' ')
        x_coord.append(float(coord_str[0]))
        y_coord.append(float(coord_str[1]))
    return x_coord,y_coord

def prase_poi_geometry(poi_geometry_str):
    geometry=poi_geometry_str.replace('POLYGON','')
    geometry=geometry.replace('(','')
    geometry = geometry.replace(')', '')
    geometry = geometry.split(',')
    x_coord=[]
    y_coord=[]
    for id in range(len(geometry)):
        coord_str = geometry[id].lstrip()
        coord_str = coord_str.split(' ')
        x_coord.append(float(coord_str[0]))
        y_coord.append(float(coord_str[1]))
    return x_coord,y_coord