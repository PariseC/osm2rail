import osmium
from .classes import *
from .settings import *


def _get_bounds(filename, bbox):
    try:
        f = osmium.io.Reader(filename)
    except:
        sys.exit(f'Error: filepath {filename} contains invalid characters. Please use english characters only')

    if bbox is None:
        header = f.header()
        box = header.box()
        bottom_left = box.bottom_left
        top_right = box.top_right
        try:
            min_lat, min_lon = bottom_left.lat, bottom_left.lon
            max_lat, max_lon = top_right.lat, top_right.lon
        except:
            min_lat, min_lon = default_bounds['min_lat'], default_bounds['min_lon']
            max_lat, max_lon = default_bounds['max_lat'], default_bounds['max_lon']

    else:
        min_lat, max_lat,min_lon, max_lon = bbox

    bounds = geometry.Polygon([(min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat), (min_lon, min_lat)])
    return bounds

class NWRHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.check_boundary = True
        self.bounds = None

        self.target_elements = None

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}

        self.osm_relation_way_dict={}

    def node(self, n):
        node = Node()
        node.osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        node.x_coord=lon
        node.y_coord=lat
        if self.check_boundary:
            if not node.geometry.within(self.bounds):
                node.in_region = False

        self.osm_node_id_list.append(node.osm_node_id)
        self.osm_node_coord_list.append((lon, lat))

        node.osm_railway = n.tags.get('railway')
        node.access=n.tags.get('access')
        node.description=n.tags.get('description')
        node.level_crossing=n.tags.get('level_crossing')
        self.osm_node_dict[node.osm_node_id] = node
        del n

    def way(self, w):
        way = Way()
        way.osm_way_id = str(w.id)
        way.ref_node_id_list = [str(node.ref) for node in w.nodes]
        railway = w.tags.get('railway')
        landuse=w.tags.get('landuse')
        if railway =='rail':
            way.railway = railway
            way.name = w.tags.get('name')
            way.electrified = w.tags.get('electrified')
            way.frequency = w.tags.get('frequency')
            way.highspeed = w.tags.get('highspeed')
            way.maxspeed = w.tags.get('maxspeed')
            way.maxspeed_designed = w.tags.get('maxspeed:designed')
            way.passenger_lines = w.tags.get('passenger_lines')
            way.railway_ctcs = w.tags.get('railway:ctcs')
            way.railway_traffic_mode = w.tags.get('railway:traffic_mode')
            way.start_date = w.tags.get('start_date')
            way.usage = w.tags.get('usage')
            way.voltage = w.tags.get('voltage')
            way.service = w.tags.get('service')
            way.gauge = w.tags.get('gauge')
        elif railway =='platform':
            way.railway = railway
            way.is_poi=True
            way.name = w.tags.get('name')
        elif railway is None and landuse is not None:
            if landuse in railway_poi_set:
                way.landuse=landuse
                way.railway=landuse
                if w.tags.get('name'):
                    way.name=w.tags.get('name')
                elif w.tags.get('operator'):
                    way.name=w.tags.get('operator')
                if way.name:
                    way.is_poi=True
            elif landuse == 'industrial' and w.tags.get('industrial'):
                industrial=w.tags.get('industrial')
                if industrial in railway_poi_set:
                    if w.tags.get('name'):
                        way.name=w.tags.get('name')
                    elif w.tags.get('operator'):
                        way.name = w.tags.get('operator')
                    if way.name:
                        way.is_poi = True
                        way.landuse='railway'
                    way.railway = industrial
        self.osm_way_dict[way.osm_way_id] = way
        del w
    def relation(self,r):
        if self.check_field_matching(r.tags.get('name'),r.tags.get('alt_name')) :
            for member in r.members:
                try:
                    member_id, member_type, member_role = member.ref, member.type, member.role
                    member_id_str = str(member_id)
                    member_type_lc = member_type.lower()
                    if member_type_lc == 'w':
                        osm_way = self.osm_way_dict[member_id_str]
                        self.osm_relation_way_dict[osm_way.osm_way_id]=osm_way
                except:
                    pass
        del r

    def check_field_matching(self,r_name,alt_r_name):
        if r_name and alt_r_name:
            if r_name in self.target_elements or alt_r_name in self.target_elements:
                return True
            else:
                for v in self.target_elements:
                    if v in r_name or v in alt_r_name:
                        return True
                return False
        elif r_name and not alt_r_name:
            if r_name in self.target_elements:
                return True
            else:
                for v in self.target_elements:
                    if v in r_name:
                        return True
                return False
        else:
            return False

def _process_ways(net, h,check_name):
    if check_name:
        for osm_way_id, osm_way in h.osm_relation_way_dict.items():
            if osm_way.railway:
                try:
                    osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
                    net.osm_way_dict[osm_way_id] = osm_way
                except KeyError as e:
                    print(
                        f'  warning: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')
    else:
        for osm_way_id, osm_way in h.osm_way_dict.items():
            if osm_way.railway:
                try:
                    osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
                    net.osm_way_dict[osm_way_id] = osm_way
                except KeyError as e:
                    print(f'  warning: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')

def read_osm_file(filename, check_boundary,target_elements,check_name, bbox):
    net = Network()

    net.bounds = _get_bounds(filename, bbox)

    h = NWRHandler()
    h.check_boundary = check_boundary
    h.bounds = net.bounds
    h.target_elements = target_elements
    h.apply_file(filename)

    net.osm_node_dict=h.osm_node_dict
    _process_ways(net,h,check_name)


    return net