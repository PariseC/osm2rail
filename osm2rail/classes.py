from .utils import get_distance_from_coord
from shapely import geometry

class Node:
    def __init__(self):
        self.name = None
        self.node_id = 0
        self.osm_node_id = None

        self.x_coord=None
        self.y_coord=None
        self.geometry = None

        self.level_crossing=None
        self.access=None
        self.description=None
        self.osm_railway=None

        self.in_region=True
        self.valid = False

        self.incoming_link_list = []
        self.outgoing_link_list = []

class Link:
    def __init__(self):
        self.link_id = 0
        self.osm_way_id = None      # str
        self.name = ''
        self.loc_name=''
        self.link_type_name = None
        self.from_node = None
        self.to_node = None

        self.railway=None
        self.geometry_str=None
        self.geometry = None

        self.length=None
        self.electrified = None
        self.frequency = None
        self.highspeed = None
        self.maxspeed = None
        self.maxspeed_designed = None
        self.passenger_lines = None
        self.railway_ctcs = None
        self.railway_traffic_mode = None
        self.start_date = None
        self.usage = None
        self.voltage = None
        self.gauge=None
        self.service=None

    def calculateLength(self):
        self.length=get_distance_from_coord(self.from_node.x_coord,self.from_node.y_coord,
                                              self.to_node.x_coord,self.to_node.y_coord) * 1000
    def generate_geometry(self):
        self.geometry=geometry.LineString([self.from_node.geometry,self.to_node.geometry])

class POI:
    def __init__(self):
        self.poi_id = 0
        self.osm_way_id = None
        self.name = None
        self.geometry = None
        self.ref_node_list=[]

    def generate_geometry(self):
        self.geometry = geometry.Polygon(self.ref_node_list)


class Way:
    def __init__(self):
        self.osm_way_id = None          # string
        self.name=''
        self.railway = ''

        self.electrified=''
        self.frequency=None
        self.highspeed=None
        self.maxspeed=None
        self.maxspeed_designed=None
        self.passenger_lines=None
        self.railway_ctcs=None
        self.railway_traffic_mode=None
        self.start_date=None
        self.usage=None
        self.voltage=None
        self.service=None
        self.landuse=None
        self.gauge=None
        self.is_poi =None
        self.layer=None
        self.ref_node_list = []

class Network:
    def __init__(self):
        self.bounds = None
        self.central_lon = 0.0
        self.central_lat = 0.0

        self.osm_node_dict = {}
        self.osm_way_dict = {}

        self.node_dict = {}
        self.link_dict = {}
        self.POI_list = []

        self.central_lon=None

        self.number_of_links=0