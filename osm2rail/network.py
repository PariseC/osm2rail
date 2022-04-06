import copy
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
    try:
        maxspeed=way.maxspeed.split(' ')
        if len(maxspeed)>1:
            link.free_speed=float(maxspeed[0])*1.6
        else:
            link.free_speed = float(maxspeed[0])
    except:
        if link.highspeed and link.railway_traffic_mode == 'passenger':
            link.free_speed = 250
        elif not link.highspeed and link.railway_traffic_mode == 'passenger':
            link.free_speed = 160
        else:
            link.free_speed = 80

    link.maxspeed_designed = way.maxspeed_designed
    link.voltage = way.voltage
    link.usage = way.usage
    link.start_date = way.start_date
    link.railway_ctcs = way.railway_ctcs
    link.highspeed = way.highspeed if way.highspeed else 'no'
    link.from_node.outgoing_link_list.append(link)
    link.to_node.incoming_link_list.append(link)
    link.calculateLength()
    link.generate_geometry()
    if link.free_speed in train_speed_list:
        link.capacity=60/block_train_headway[link.free_speed]
    elif link.free_speed<train_speed_list[0]:
        link.capacity=60/block_train_headway[train_speed_list[0]]
    elif link.free_speed>train_speed_list[-1]:
        link.capacity=60/block_train_headway[train_speed_list[-1]]
    else:
        for k in range(1,len(train_speed_list)):
            if train_speed_list[k-1]<link.free_speed<train_speed_list[k]:
                link.capacity=60/train_speed_list[k]
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
        if len(way.ref_node_list)<=2:
            continue
        poi.ref_node_list = ref_node_list
        poi.generate_geometry()
        poi.area=poi.geometry.area
        lon, lat = poi.geometry.centroid.x, poi.geometry.centroid.y
        poi.centroid = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        POI_list.append(poi)
        poi_id += 1
        network.POI_list.append(poi)

def _create_NLPs(network,POIs):
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

def _buildNet(network,check_boundary=False,POIs=False):
    _create_NLPs(network,POIs)
    _filter_osm_node(network)
    if check_boundary:
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

def create_micro_net(network,mic_link_length=10,recursionlimit=5000):
    link_id=0
    node_id=0
    sys.setrecursionlimit(recursionlimit)
    for _, link in network.link_dict.items():
        from_node=link.from_node
        to_node=link.to_node
        detla_x=to_node.x_coord-from_node.x_coord
        detla_y=to_node.y_coord-from_node.y_coord
        length=link.length
        number_of_micro_links=int(round(length/mic_link_length,0))
        if number_of_micro_links<=1:
            micro_f_node=copy.deepcopy(from_node)
            micro_f_node.node_id=node_id
            node_id+=1
            micro_t_node=copy.deepcopy(to_node)
            micro_t_node.node_id=node_id
            node_id+=1
            network.micro_node_list.append(micro_f_node)
            network.micro_node_list.append(micro_t_node)
            micro_link=copy.deepcopy(link)
            micro_link.link_id=link_id
            link_id+=1
            network.micro_link_list.append(micro_link)
        else:
            for n in range(number_of_micro_links):
                if n == 0:
                    micro_f_node=copy.deepcopy(from_node)
                    micro_f_node.node_id=node_id
                    node_id+=1
                else:
                    micro_f_node=Node()
                    micro_f_node.node_id=node_id
                    node_id+=1
                    lon=from_node.x_coord+detla_x*(n/number_of_micro_links)
                    lat=from_node.y_coord+detla_y*(n/number_of_micro_links)
                    micro_f_node.x_coord=lon
                    micro_f_node.y_coord=lat
                    micro_f_node.geometry=geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
                if n == number_of_micro_links-1:
                    micro_t_node=copy.deepcopy(to_node)
                    micro_t_node.node_id=node_id
                    node_id+=1
                else:
                    micro_t_node=Node()
                    micro_t_node.node_id=node_id
                    node_id+=1
                    lon=from_node.x_coord+detla_x*((n+1)/number_of_micro_links )
                    lat=from_node.y_coord+detla_y*((n+1)/number_of_micro_links )
                    micro_t_node.x_coord=lon
                    micro_t_node.y_coord=lat
                    micro_t_node.geometry=geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
                micro_link=copy.deepcopy(link)
                micro_link.from_node=micro_f_node
                micro_link.to_node=micro_t_node
                micro_link.generate_geometry()
                micro_link.calculateLength()
                micro_link.link_id=link_id
                micro_link.main_link_id=link.link_id
                link_id+=1
                network.micro_link_list.append(micro_link)
                network.micro_node_list.append(micro_f_node)
                network.micro_node_list.append(micro_t_node)

def get_network_from_file(filename='map.osm',bbox=None,check_boundary=False,target_elements=None,POIs=False):
    """
    :param filename: str,.osm or .osm.pbf file path.
    :param bbox: tuble(min_lat, max_lat,min_lon, max_lon).
    :param check_boundary: bool.
    :param target_elements: str or list.
    :param POIs: bool
    :return:
    """
    filename,is_tmp=_check_filename(filename)
    if isinstance(target_elements,str):
        target_elements_=[target_elements]
        check_name = True
    elif isinstance(target_elements,list):
        target_elements_=target_elements
        check_name = True
    else:
        target_elements_= []
        check_name =False
    network=read_osm_file(filename=filename,check_boundary=check_boundary,target_elements=target_elements_,
                        check_name=check_name,bbox=bbox)

    _buildNet(network=network,check_boundary=check_boundary,POIs=POIs)
    if is_tmp:
        os.remove(filename)
    return network

