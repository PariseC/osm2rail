import os
import pathlib
import tempfile
import shutil
from .reader import *

def _new_link_from_way(from_node,to_node, way):
    link = Link()
    link.osm_way_id = way.osm_way_id
    link.name = way.name
    link.link_type_name = way.railway
    link.from_node = from_node
    link.to_node = to_node
    link.railway = way.railway
    link.frequency = way.frequency
    link.gauge = way.gauge
    link.passenger_lines = way.passenger_lines
    link.railway_traffic_mode = way.railway_traffic_mode
    link.service = way.service
    link.electrified = way.electrified
    link.maxspeed = way.maxspeed
    link.maxspeed_designed = way.maxspeed_designed
    link.voltage = way.voltage
    link.usage = way.usage
    link.start_date = way.start_date
    link.railway_ctcs = way.railway_ctcs
    link.highspeed = way.highspeed
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    link.calculateLength()
    link.generate_geometry()
    return link

def _create_links(network, link_way_list):
    link_id = 0
    for way in link_way_list:
        for ref_node_id in range(len(way.ref_node_list) - 1):
            from_node = way.ref_node_list[ref_node_id]
            from_node.valid = True
            to_node = way.ref_node_list[ref_node_id + 1]
            to_node.valid = True
            link=_new_link_from_way(from_node,to_node, way)
            link.link_id=link_id
            network.link_dict[link_id]=link
            link_id+=1
    network.number_of_links = link_id

def _create_pois(network,POI_way_list):
    POI_list = []
    poi_id = 0
    for way in POI_way_list:
        poi = POI()
        poi.poi_id = poi_id
        poi.name = way.name
        poi.railway = way.railway
        poi.osm_way_id = way.osm_way_id
        ref_node_list = []
        for ref_node in way.ref_node_list:
            # ref_node.valid=True
            ref_node_list.append(ref_node.geometry)
        if way.ref_node_list[0].osm_node_id != way.ref_node_list[-1].osm_node_id:
            continue
        poi.ref_node_list = ref_node_list
        poi.generate_geometry()
        POI_list.append(poi)
        poi_id += 1
        network.POI_list.append(poi)

def _createNLPs(network,POIs):
    link_way_list = []
    POI_way_list = []
    for osm_way_id,way in network.osm_way_dict.items():
        if way.is_poi:
            POI_way_list.append(way)
        else:
            link_way_list.append(way)
    if len(link_way_list):
        _create_links(network, link_way_list)
    else:
        print('railway link not found')
    if POIs:
        if len(POI_way_list)>0:
            _create_pois(network,POI_way_list)
        else:
            print('railway POI not found')

def _filter_osm_node(network):
    node_dict = {}
    node_id = 0
    for osm_node_id, node in network.osm_node_dict.items():
        if node.valid and node.in_region:
            node.node_id = node_id
            node_dict[node_id] = node
            node_id += 1
    network.node_dict = node_dict

def _filter_osm_link(network):
    link_dict = {}
    link_id = 0
    for id, link in network.link_dict.items():
        from_node = link.from_node
        to_node = link.to_node
        if from_node.in_region and to_node.in_region:
            link_dict[link_id] = link
            link_id = link_id + 1
    network.link_dict = link_dict

def _filter_osm_poi(network):
    poi_list = []
    for poi in network.POI_list:
        if poi.geometry.within(network.bounds):
            poi_list.append(poi)
    network.POI_list = poi_list

def _buildNet(network,strict_mode=False,POIs=False):
    _createNLPs(network,POIs)
    _filter_osm_node(network)
    if strict_mode:
        _filter_osm_link(network)
        _filter_osm_poi(network)

def _check_filename(filename):
    path = pathlib.Path(filename)
    for ch in filename:
        if '\u4e00' <= ch <= '\u9fff':
            # 获取临时文件夹
            tmpdir = tempfile.gettempdir()
            if path.suffix == '.pbf':
                tmpfile=os.path.join(tmpdir,'map.osm.pbf')
            else:
                tmpfile=os.path.join(tmpdir,'map.osm')
            shutil.copy(filename,tmpfile)
            return tmpfile,True
    return filename,False

def get_network_from_file(filename='map.osm',bbox=None,strict_mode=False,POIs=False):
    filename,is_tmp=_check_filename(filename)
    network=readOSMFile(filename=filename,strict_mode=strict_mode,bbox=bbox)
    _buildNet(network=network,strict_mode=strict_mode,POIs=POIs)
    if is_tmp:
        os.remove(filename)
    return network