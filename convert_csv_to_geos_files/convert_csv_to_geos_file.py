# -*- coding: utf-8 -*-
# @Time    : 2022/4/14 21:01
# @Author  : Praise
# @File    : convert_csv_to_geos_file.py
# obj:
import sys
import geopandas as gpd
import pandas as pd
import os
from shapely import geometry
from shapely.wkt import loads

def converter(node_file,link_file,poi_file,out_folder=None,format='.shp',crs='EPSG:4326'):
    """
    :param node_file:
    :param link_file:
    :param poi_file:
    :param out_folder:
    :param format: str, '.shp', '.gpkg', '.geojson'
    :return:
    """
    if format not in ['.shp','.gpkg','.geojson']:
        print('It is recommended to select the file format from [{},{},{}]'.format('.shp','.gpkg','.geojson'))
        sys.exit()
    if out_folder:
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        node_file_ = os.path.join(out_folder,'node' + format)
        link_file_ = os.path.join(out_folder,'link' + format)
        poi_file_ = os.path.join(out_folder, 'poi' + format)
    else:
        node_file_ = 'node'+format
        link_file_ = 'link'+format
        poi_file_ = 'poi'+format
    "read and convert node csv to geos file"
    try:
        df_node = pd.read_csv(node_file)
        cols = df_node.columns.tolist()
        cols.remove('x_coord')
        cols.remove('y_coord')
        if format == '.shp':
            cols_ = []
            for col in cols:
                if len(col.encode('utf-8')) > 10:
                    print("Warning: the length of '{}' exceeds the maximum limit and has been ignored".format(col))
                else:
                    cols_.append(col)
            cols = cols_
        node_attrs = df_node[cols].values.tolist()
        node_geometry_str = df_node[ ['x_coord','y_coord']].values.tolist()
        node_geometry = [ geometry.Point(x,y) for (x,y) in node_geometry_str ]
        geo_df_node = gpd.GeoDataFrame(
            data=node_attrs,
            geometry=node_geometry,
            columns=cols,
            crs=crs,
        )
    except Exception as e:
        print(e)
    "read and convert link csv to geos file"
    try:
        df_link = pd.read_csv(link_file)
        cols = df_link.columns.tolist()
        cols.remove('geometry')
        if format == '.shp':
            cols_ = []
            for col in cols:
                if len(col.encode('utf-8')) > 10:
                    print("Warning: the length of '{}' exceeds the maximum limit and has been ignored".format(col))
                else:
                    cols_.append(col)
            cols = cols_
        link_attrs = df_link[cols].values.tolist()
        link_geometry_str = df_link['geometry'].values.tolist()
        link_geometry = [loads(link_geo) for link_geo in link_geometry_str]
        geo_df_link = gpd.GeoDataFrame(
            data=link_attrs,
            geometry=link_geometry,
            columns=cols,
            crs=crs,
        )
    except Exception as e:
        print(e)
    "read and convert poi csv to geos file"
    try:
        df_poi = pd.read_csv(poi_file)
        cols = df_poi.columns.tolist()
        cols.remove('geometry')
        if format == '.shp':
            cols_ = []
            for col in cols:
                if len(col.encode('utf-8')) > 10:
                    print("Warning: the length of '{}' exceeds the maximum limit and has been ignored".format(col))
                else:
                    cols_.append(col)
            cols = cols_
        poi_attrs = df_poi[cols].values.tolist()
        poi_geometry_str = df_poi['geometry'].values.tolist()
        poi_geometry = [loads(poi_geo) for poi_geo in poi_geometry_str]
        geo_df_poi = gpd.GeoDataFrame(
            data=poi_attrs,
            geometry=poi_geometry,
            columns=cols,
            crs=crs,
        )
    except Exception as e:
        print(e)
    try:
        if format == '.shp':
            geo_df_node.to_file(node_file_,index=False)
            geo_df_link.to_file(link_file_,index=False)
            geo_df_poi.to_file(poi_file_,index=False)
        elif format == '.gpkg':
            geo_df_node.to_file(node_file_,driver='GPKG',index=False)
            geo_df_link.to_file(link_file_,driver='GPKG',index=False)
            geo_df_poi.to_file(poi_file_,driver='GPKG',index=False)
        else:
            geo_df_node.to_file(node_file_, driver='GeoJSON',index=False)
            geo_df_link.to_file(link_file_, driver='GeoJSON',index=False)
            geo_df_poi.to_file(poi_file_, driver='GeoJSON',index=False)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    node_file = r'./node.csv'
    link_file = r'./link.csv'
    poi_file = r'./poi.csv'
    converter(node_file,link_file,poi_file,out_folder='./geojson',format='.geojson')