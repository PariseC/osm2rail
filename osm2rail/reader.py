import numpy as np
from .readfile import *
from .classes import *
from shapely import geometry


def filter_osm_poi(network):
    poi_list = []
    for poi in network.POI_list:
        if poi.geometry.within(network.bounds):
            poi_list.append(poi)
    network.POI_list = poi_list

def filter_osm_link(network):
        link_dict={}
        link_id=0
        for id,link in network.link_dict.items():
            from_node=link.from_node
            to_node=link.to_node
            if from_node.in_region and to_node.in_region:
                link_dict[link_id]=link
                link_id=link_id+1
        network.link_dict=link_dict

def filter_osm_node(network):
    node_dict = {}
    node_id = 0
    for osm_node_id, node in network.osm_node_dict.items():
        if node.valid and node.in_region:
            node.node_id = node_id
            node_dict[node_id] = node
            node_id += 1
    network.node_dict = node_dict

def create_pois(POI_way_list):
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
    return POI_list, poi_id

def new_link_from_way(link_id, way):
    link_list = []
    for ref_node_id in range(len(way.ref_node_list) - 1):
        from_node = way.ref_node_list[ref_node_id]
        from_node.valid = True
        to_node = way.ref_node_list[ref_node_id + 1]
        to_node.valid = True
        link = Link()
        link.osm_way_id = way.osm_way_id
        link.link_id = link_id
        link.name = way.name
        link.link_type_name = way.railway
        link.from_node = from_node
        link.to_node = to_node
        link.frequency = way.frequency
        link.gauge = way.gauge
        link.passenger_lines = way.passenger_lines
        link.railway_traffic_mode = way.railway_traffic_mode
        link.service = way.service
        link.electrified = way.electrified
        link.maxspeed = way.maxspeed
        link.maxspeed_designed = way.maxspeed_designed
        link.from_node.outgoing_link_list.append(link)
        link.to_node.incoming_link_list.append(link)
        link.calculateLength()
        link.generate_geometry()
        link_list.append(link)
        link_id += 1
    return link_list

def create_links(network, link_way_list):
    link_dict = {}
    link_id = network.number_of_links
    for way in link_way_list:
        link_list = new_link_from_way(link_id, way)
        for link in link_list:
            link_dict[link.link_id] = link
            link_id += 1
    network.link_dict = link_dict
    network.number_of_links = link_id

def parse_ways(network, ways, POIs):
    osm_way_dict = {}
    osm_node_dict = network.osm_node_dict

    for osm_way in ways:
        way = Way()
        way.osm_way_id = str(osm_way.id)

        valid = True
        for ref_node_id in osm_way.refs:
            try:
                way.ref_node_list.append(osm_node_dict[str(ref_node_id)])
            except KeyError:
                valid = False
                print(
                    f'  warning: ref node {ref_node_id} in way {way.osm_way_id} is not defined, way {way.osm_way_id} will not be imported')
        if not valid:
            continue

        tags = osm_way.tags
        # filter subway and tram mode
        if 'railway' in tags.keys() and 'subway' not in tags.keys() and 'tram' not in tags.keys():
            if tags['railway'] in railway_object:
                way.railway = tags['railway']
                if way.railway in railway_poi_set:
                    way.way_poi = way.railway
                if 'name' in tags.keys():
                    way.name = tags['name']
                if 'electrified' in tags.keys():
                    way.electrified = tags['electrified']
                if 'frequency' in tags.keys():
                    way.frequency = tags['frequency']
                if 'highspeed' in tags.keys():
                    way.highspeed = tags['highspeed']
                if 'maxspeed' in tags.keys():
                    way.maxspeed = tags['maxspeed']
                if 'maxspeed:designed' in tags.keys():
                    way.maxspeed_designed = tags['maxspeed:designed']
                if 'passenger_lines' in tags.keys():
                    way.passenger_lines = tags['passenger_lines']
                if 'railway:ctcs' in tags.keys():
                    way.railway_ctcs = tags['railway:ctcs']
                if 'railway:traffic_mode' in tags.keys():
                    way.railway_traffic_mode = tags['railway:traffic_mode']
                if 'start_date' in tags.keys():
                    way.start_date = tags['start_date']
                if 'usage' in tags.keys():
                    way.usage = tags['usage']
                if 'voltage' in tags.keys():
                    way.voltage = tags['voltage']
                if 'gauge' in tags.keys():
                    way.gauge = tags['gauge']
                if 'service' in tags.keys():
                    way.service = tags['service']
                osm_way_dict[way.osm_way_id] = way
        elif 'railway' not in tags.keys() and 'landuse' in tags.keys():
            if tags['landuse'] in railway_object:
                way.landuse = tags['landuse']
                if 'name' in tags.keys():
                    way.name = tags['name']
                elif 'operator' in tags.keys():
                    way.name = tags['operator']
                if way.name:
                    way.way_poi = way.name
                    osm_way_dict[way.osm_way_id] = way
            elif tags['landuse'] == 'industrial' and 'industrial' in tags.keys():
                if tags['industrial'] in railway_object:
                    if 'name' in tags.keys():
                        way.name = tags['name']
                    elif 'operator' in tags.keys():
                        way.name = tags['operator']
                    if way.name:
                        way.way_poi = way.name
                        way.landuse = 'railway'
                        osm_way_dict[way.osm_way_id] = way

    network.osm_way_dict = osm_way_dict

    link_way_list = []
    POI_way_list = []

    for osm_way_id, way in osm_way_dict.items():
        if way.way_poi:
            POI_way_list.append(way)
        else:
            way.link_type_name = way.railway
            link_way_list.append(way)

    # self.get_network_nodes(network)  # osm node -> node
    if len(link_way_list):
        create_links(network, link_way_list)
    else:
        print('railway link not found')
        return
    if POIs:
        if len(POI_way_list):
            network.POI_list, network.max_poi_id = create_pois(POI_way_list)
        else:
            print('railway POI not found')

def parse_nodes(network, nodes, strict_mode):
    osm_node_dict = {}
    osm_node_coord_list = []

    for osm_node in nodes:
        node = Node()
        node.osm_node_id = str(osm_node.id)
        lon, lat = osm_node.lonlat
        node.x_coord = lon
        node.y_coord = lat
        node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        if strict_mode:
            if node.geometry.within(network.bounds):
                node.in_region = True
        else:
            node.in_region = True

        osm_node_coord_list.append((lon, lat))

        tags = osm_node.tags
        if 'railway' in tags.keys():
            node.railway = tags['railway']
        if 'name' in tags.keys():
            node.name = tags['name']
        if 'level_crossing' in tags.keys():
            node.level_crossing = tags['level_crossing']
        if 'access' in tags.keys():
            node.access = tags['access']
        if 'description' in tags.keys():
            node.description = tags['description']

        osm_node_dict[node.osm_node_id] = node

    coord_array = np.array(osm_node_coord_list)
    central_lon = coord_array[:, 0].mean()
    network.central_lon = central_lon

    network.osm_node_dict = osm_node_dict

def parse_OSM(network, nodes, ways, strict_mode, POIs):
    parse_nodes(network, nodes, strict_mode)
    parse_ways(network, ways, POIs)
    filter_osm_node(network)
    if strict_mode:
        filter_osm_link(network)
        filter_osm_poi(network)

def build_network(netdata, strict_mode, bbox, POIs):
    network = Network()

    bounds, nodes, ways = netdata['bounds'], netdata['nodes'], netdata['ways']

    minlat, minlon, maxlat, maxlon = bbox if bbox else bounds['minlat'], bounds['minlon'], bounds['maxlat'], bounds[
        'maxlon']
    network.bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])

    parse_OSM(network, nodes, ways, strict_mode, POIs)

    return network

def get_network_from_OSMFile(osm_filename,bbox=None,strict_mode=False,POIs=False ):
    netdata = readXMLFile(osm_filename)
    network = build_network(netdata,strict_mode,bbox, POIs)
    return network

def get_network_from_PBFFile(pbf_filename,bbox=None,strict_mode=False, POIs=False):
    netdata = readPBFFile(pbf_filename)
    network = build_network(netdata,strict_mode, bbox,POIs)
    return network

class NetworkReader():
    def __init__(self):
        pass

    def build_network(self,netdata,strict_mode,bbox,POIs):
        network = Network()

        bounds, nodes, ways= netdata['bounds'], netdata['nodes'], netdata['ways']

        minlat, minlon, maxlat, maxlon = bbox if bbox else bounds['minlat'], bounds['minlon'], bounds['maxlat'], bounds['maxlon']
        network.bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])

        self.__parse_OSM(network, nodes, ways,strict_mode,POIs)


        return network

    def __parse_OSM(self,network, nodes, ways,strict_mode,POIs):
        self.__parse_nodes(network, nodes,strict_mode)
        self.__parse_ways(network, ways,POIs)
        self.__filter_osm_node(network)
        if strict_mode:
            self.__filter_osm_link(network)
            self.__filter_osm_poi(network)

    def __parse_nodes(self,network, nodes,strict_mode):
        osm_node_dict = {}
        osm_node_coord_list = []

        for osm_node in nodes:
            node = Node()
            node.osm_node_id = str(osm_node.id)
            lon, lat = osm_node.lonlat
            node.x_coord=lon
            node.y_coord=lat
            node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
            if strict_mode:
                if node.geometry.within(network.bounds):
                    node.in_region=True
            else:
                node.in_region = True

            osm_node_coord_list.append((lon, lat))

            tags = osm_node.tags
            if 'railway' in tags.keys():
                node.railway = tags['railway']
            if 'name' in tags.keys():
                node.name=tags['name']
            if 'level_crossing' in tags.keys():
                node.level_crossing=tags['level_crossing']
            if 'access' in tags.keys():
                node.access=tags['access']
            if 'description' in tags.keys():
                node.description=tags['description']

            osm_node_dict[node.osm_node_id] = node

        coord_array = np.array(osm_node_coord_list)
        central_lon = coord_array[:, 0].mean()
        network.central_lon = central_lon

        network.osm_node_dict = osm_node_dict

    def __parse_ways(self,network, ways,POIs):
        osm_way_dict = {}
        osm_node_dict = network.osm_node_dict

        for osm_way in ways:
            way = Way()
            way.osm_way_id = str(osm_way.id)

            valid = True
            for ref_node_id in osm_way.refs:
                try:
                    way.ref_node_list.append(osm_node_dict[str(ref_node_id)])
                except KeyError:
                    valid = False
                    print(
                        f'  warning: ref node {ref_node_id} in way {way.osm_way_id} is not defined, way {way.osm_way_id} will not be imported')
            if not valid:
                continue

            tags = osm_way.tags
            # filter subway and tram mode
            if 'railway' in tags.keys() and 'subway' not in tags.keys() and 'tram' not in tags.keys():
                if tags['railway'] in railway_object:
                    way.railway = tags['railway']
                    if way.railway in railway_poi_set:
                        way.way_poi = way.railway
                    if 'name' in tags.keys():
                        way.name=tags['name']
                    if 'electrified' in tags.keys():
                        way.electrified=tags['electrified']
                    if 'frequency' in tags.keys():
                        way.frequency=tags['frequency']
                    if 'highspeed' in tags.keys():
                        way.highspeed=tags['highspeed']
                    if 'maxspeed' in tags.keys():
                        way.maxspeed=tags['maxspeed']
                    if 'maxspeed:designed' in tags.keys():
                        way.maxspeed_designed=tags['maxspeed:designed']
                    if 'passenger_lines' in tags.keys():
                        way.passenger_lines=tags['passenger_lines']
                    if 'railway:ctcs' in tags.keys():
                        way.railway_ctcs=tags['railway:ctcs']
                    if 'railway:traffic_mode' in tags.keys():
                        way.railway_traffic_mode=tags['railway:traffic_mode']
                    if 'start_date' in tags.keys():
                        way.start_date=tags['start_date']
                    if 'usage' in tags.keys():
                        way.usage=tags['usage']
                    if 'voltage' in tags.keys():
                        way.voltage=tags['voltage']
                    if 'gauge' in tags.keys():
                        way.gauge=tags['gauge']
                    if 'service' in tags.keys():
                        way.service=tags['service']
                    osm_way_dict[way.osm_way_id] = way
            elif 'railway' not in tags.keys() and 'landuse' in tags.keys():
                if tags['landuse'] in railway_object:
                    way.landuse=tags['landuse']
                    if 'name' in tags.keys():
                        way.name = tags['name']
                    elif 'operator' in tags.keys():
                        way.name=tags['operator']
                    if way.name:
                        way.way_poi = way.name
                        osm_way_dict[way.osm_way_id] = way
                elif tags['landuse']=='industrial' and 'industrial' in tags.keys():
                    if tags['industrial'] in railway_object:
                        if 'name' in tags.keys():
                            way.name = tags['name']
                        elif 'operator' in tags.keys():
                            way.name = tags['operator']
                        if way.name:
                            way.way_poi = way.name
                            way.landuse='railway'
                            osm_way_dict[way.osm_way_id] = way


        network.osm_way_dict = osm_way_dict

        link_way_list = []
        POI_way_list = []

        for osm_way_id, way in osm_way_dict.items():
            if way.way_poi:
                POI_way_list.append(way)
            else:
                way.link_type_name = way.railway
                link_way_list.append(way)


        # self.get_network_nodes(network)  # osm node -> node
        if len(link_way_list):
            self.__create_links(network, link_way_list)
        else:
            print('railway link not found')
            return
        if POIs:
            if len(POI_way_list):
                network.POI_list,network.max_poi_id =self.__create_pois(POI_way_list)
            else:
                print('railway POI not found')

    def __create_links(self,network, link_way_list):
        link_dict = {}
        link_id = network.number_of_links
        for way in link_way_list:
            link_list = self.__new_link_from_way(link_id, way)
            for link in link_list:
                link_dict[link.link_id]=link
                link_id+= 1
        network.link_dict=link_dict
        network.number_of_links=link_id

    def __new_link_from_way(self,link_id,way):
        link_list = []
        for ref_node_id in range(len(way.ref_node_list) - 1):
            from_node = way.ref_node_list[ref_node_id]
            from_node.valid = True
            to_node = way.ref_node_list[ref_node_id + 1]
            to_node.valid = True
            link = Link()
            link.osm_way_id = way.osm_way_id
            link.link_id=link_id
            link.name = way.name
            link.link_type_name = way.railway
            link.from_node = from_node
            link.to_node = to_node
            link.frequency = way.frequency
            link.gauge = way.gauge
            link.passenger_lines = way.passenger_lines
            link.railway_traffic_mode = way.railway_traffic_mode
            link.service = way.service
            link.electrified = way.electrified
            link.maxspeed = way.maxspeed
            link.maxspeed_designed = way.maxspeed_designed
            link.from_node.outgoing_link_list.append(link)
            link.to_node.incoming_link_list.append(link)
            link.calculateLength()
            link.generate_geometry()
            link_list.append(link)
            link_id+=1
        return link_list

    def __create_pois(self,POI_way_list):
        POI_list=[]
        poi_id=0
        for way in POI_way_list:
            poi=POI()
            poi.poi_id=poi_id
            poi.name=way.name
            poi.railway=way.railway
            poi.osm_way_id=way.osm_way_id
            ref_node_list=[]
            for ref_node in way.ref_node_list:
                # ref_node.valid=True
                ref_node_list.append(ref_node.geometry)
            if way.ref_node_list[0].osm_node_id!=way.ref_node_list[-1].osm_node_id:
                continue
            poi.ref_node_list=ref_node_list
            poi.generate_geometry()
            POI_list.append(poi)
            poi_id+=1
        return POI_list,poi_id

    def __filter_osm_node(self,network):
        node_dict={}
        node_id=0
        for osm_node_id,node in network.osm_node_dict.items():
            if node.valid and node.in_region:
                node.node_id=node_id
                node_dict[node_id]=node
                node_id+=1
        network.node_dict=node_dict

    def __filter_osm_link(self,network):
        link_dict={}
        link_id=0
        for id,link in network.link_dict.items():
            from_node=link.from_node
            to_node=link.to_node
            if from_node.in_region and to_node.in_region:
                link_dict[link_id]=link
                link_id=link_id+1
        network.link_dict=link_dict

    def __filter_osm_poi(self,network):
        poi_list=[]
        for poi in network.POI_list:
            if poi.geometry.within(network.bounds):
                poi_list.append(poi)
        network.POI_list=poi_list


    def get_network_from_OSMFile(self,osm_filename,bbox=None,strict_mode=False,POIs=False ):

        netdata = readXMLFile(osm_filename)
        network = self.build_network(netdata,strict_mode,bbox, POIs)
        return network

    def get_network_from_PBFFile(self,pbf_filename,bbox=None,strict_mode=False, POIs=False):
        netdata = readPBFFile(pbf_filename)
        network = self.build_network(netdata,strict_mode, bbox,POIs)
        return network