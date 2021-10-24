import osmium
from .classes import *
from .settings import *


def _getBounds(filename, bbox):
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
            minlat, minlon = bottom_left.lat, bottom_left.lon
            maxlat, maxlon = top_right.lat, top_right.lon
        except:
            minlat, minlon, maxlat, maxlon = default_bounds['minlat'], default_bounds['minlon'], default_bounds['maxlat'], default_bounds['maxlon']
    else:
        minlat, maxlat,minlon, maxlon = bbox

    bounds = geometry.Polygon([(minlon, maxlat), (maxlon, maxlat), (maxlon, minlat), (minlon, minlat)])
    return bounds

class NWRHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.strict_mode = True
        self.bounds = None

        self.osm_node_dict = {}
        self.osm_node_id_list = []
        self.osm_node_coord_list = []

        self.osm_way_dict = {}

    def node(self, n):
        node = Node()
        node.osm_node_id = str(n.id)
        lon, lat = n.location.lon, n.location.lat
        node.geometry = geometry.Point((round(lon, lonlat_precision), round(lat, lonlat_precision)))
        node.x_coord=lon
        node.y_coord=lat
        if self.strict_mode:
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
        way.railway = w.tags.get('railway')
        landuse=w.tags.get('landuse')
        if way.railway =='rail':
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
            self.osm_way_dict[way.osm_way_id] = way
        elif way.railway =='platform':
                way.is_poi=True
                way.name = w.tags.get('name')
                self.osm_way_dict[way.osm_way_id] = way
        elif way.railway is None and landuse is not None:
            if landuse in railway_poi_set:
                way.landuse=landuse
                way.railway=landuse
                if w.tags.get('name'):
                    way.name=w.tags.get('name')
                elif w.tags.get('operator'):
                    way.name=w.tags.get('operator')
                if way.name:
                    way.is_poi=True
                    self.osm_way_dict[way.osm_way_id] = way
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
                        self.osm_way_dict[way.osm_way_id] = way
        del w

def _processWays(net, h):
    for osm_way_id, osm_way in h.osm_way_dict.items():
        try:
            osm_way.ref_node_list = [net.osm_node_dict[ref_node_id] for ref_node_id in osm_way.ref_node_id_list]
            net.osm_way_dict[osm_way_id] = osm_way
        except KeyError as e:
            print(f'  warning: ref node {e} in way {osm_way_id} is not defined, way {osm_way_id} will not be imported')

def readOSMFile(filename, strict_mode, bbox):
    net = Network()

    net.bounds = _getBounds(filename, bbox)

    h = NWRHandler()
    h.strict_mode = strict_mode
    h.bounds = net.bounds
    h.apply_file(filename)

    net.osm_node_dict=h.osm_node_dict
    _processWays(net,h)


    return net