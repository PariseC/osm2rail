import csv
import os
from .utils import validate_download_dir

def save_network(network, output_folder='csvfile', enconding=None):
    """

    :param network: network class
    :param output_folder: str,defaults to './csvfile'
    :param enconding: defaults to None
    :return:
    """
    validate_download_dir(output_folder)
    if output_folder:
        validate_download_dir(output_folder)
        node_filepath = os.path.join(output_folder, 'node.csv')
        link_filepath = os.path.join(output_folder, 'link.csv')
        poi_filepath = os.path.join(output_folder, 'poi.csv')

    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'
        poi_filepath = 'poi.csv'

    try:
        if enconding is None:
            outfile = open(node_filepath, 'w', newline='', errors='ignore')
        else:
            outfile = open(node_filepath, 'w', newline='', errors='ignore', encoding=enconding)

        write = csv.writer(outfile)
        write.writerow(['name', 'node_id', 'osm_node_id', 'railway', 'level_crossing', 'access', 'description',
                        'x_coord', 'y_coord', 'geometry'])

        for node_id, node in network.node_dict.items():
            name = node.name if node.name else ''
            level_crossing = node.level_crossing if node.level_crossing else ''
            access = node.access if node.access else ''
            description = node.description if node.description else ''
            railway = node.osm_railway if node.osm_railway else ''
            geometry = node.geometry.wkt
            line = [name, node.node_id, node.osm_node_id, railway, level_crossing, access, description,
                    node.x_coord, node.y_coord, geometry]
            write.writerow(line)
        outfile.close()
    except PermissionError:
        print('node.csv may be locked by other programs. please release it then try again')

    try:
        if enconding is None:
            outfile = open(link_filepath, 'w', newline='', errors='ignore')
        else:
            outfile = open(link_filepath, 'w', newline='', errors='ignore', encoding=enconding)

        write = csv.writer(outfile)
        write.writerow(['name', 'link_id', 'osm_way_id', 'from_node_id', 'to_node_id', 'link_type_name','dir_flag','electrified',
                        'frequency', 'highspeed', 'free_speed','maxspeed_designed', 'passenger_lines', 'railway_ctcs',
                        'railway_traffic_mode', 'start_date','usage', 'voltage', 'gauge', 'service', 'length','lanes','capacity',
                        'geometry'])
        link_id=0
        for _, link in network.link_dict.items():
            name = link.name if link.name else ''
            link_type_name = link.link_type_name if link.link_type_name else ''
            electrified = link.electrified if link.electrified else ''
            frequency = link.frequency if link.frequency else ''
            highspeed = link.highspeed if link.highspeed else ''
            free_speed = link.free_speed if link.free_speed else ''
            maxspeed_designed = link.maxspeed_designed if link.maxspeed_designed else ''
            passenger_lines = link.passenger_lines if link.passenger_lines else ''
            railway_ctcs = link.railway_ctcs if link.railway_ctcs else ''
            railway_traffic_mode = link.railway_traffic_mode if link.railway_traffic_mode else ''
            start_date = link.start_date if link.start_date else ''
            usage = link.usage if link.usage else ''
            voltage = link.voltage if link.voltage else ''
            gauge = link.gauge if link.gauge else ''
            service = link.service if link.service else ''
            lanes=1
            capacity=link.capacity
            line = [name, link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id,link_type_name,
                    link.dir_flag,electrified,frequency,highspeed, free_speed, maxspeed_designed, passenger_lines,
                    railway_ctcs,railway_traffic_mode,start_date, usage, voltage, gauge, service, link.length,lanes,
                    capacity,link.geometry.wkt]
            write.writerow(line)
            link_id+=1
        outfile.close()
    except PermissionError:
        print('link.csv may be locked by other programs. please release it then try again')

    try:
        if len(network.POI_list):
            if enconding is None:
                outfile = open(poi_filepath, 'w', newline='', errors='ignore')
            else:
                outfile = open(poi_filepath, 'w', newline='', errors='ignore', encoding=enconding)

            write = csv.writer(outfile)
            write.writerow(['name', 'poi_id', 'osm_way_id','building','amenity','area','geometry','centroid'])
            poi_id=0
            for poi in network.POI_list:
                name = ' ' + poi.name if poi.name else ''
                building=poi.railway if poi.railway else ''
                amenity=''
                line = [name, poi_id, poi.osm_way_id, building,amenity,poi.area, poi.geometry.wkt,poi.centroid.wkt]
                write.writerow(line)
                poi_id+=1
            outfile.close()
    except PermissionError:
        print('poi.csv may be locked by other programs. please release it then try again')

    "save micro network to csv"
    if len(network.micro_node_list)>0:
        if output_folder:
            output_folder=os.path.join(output_folder,'micro_network')
            validate_download_dir(output_folder)
            micro_node_filepath = os.path.join(output_folder, 'node.csv')
            micro_link_filepath = os.path.join(output_folder, 'link.csv')

        else:
            output_folder='./micro_network'
            validate_download_dir(output_folder)
            micro_node_filepath = os.path.join(output_folder, 'node.csv')
            micro_link_filepath = os.path.join(output_folder, 'link.csv')

        try:
            if enconding is None:
                outfile = open(micro_node_filepath, 'w', newline='', errors='ignore')
            else:
                outfile = open(micro_node_filepath, 'w', newline='', errors='ignore', encoding=enconding)

            write = csv.writer(outfile)
            write.writerow(['name', 'node_id', 'osm_node_id', 'osm_railway', 'level_crossing', 'access', 'description',
                            'x_coord', 'y_coord', 'geometry'])

            for node in network.micro_node_list:
                name = node.name if node.name else ''
                level_crossing = node.level_crossing if node.level_crossing else ''
                access = node.access if node.access else ''
                description = node.description if node.description else ''
                railway = node.osm_railway if node.osm_railway else ''
                geometry = node.geometry.wkt
                line = [name, node.node_id, node.osm_node_id, railway, level_crossing, access, description,
                        node.x_coord, node.y_coord, geometry]
                write.writerow(line)
            outfile.close()
        except PermissionError:
            print('micro node.csv may be locked by other programs. please release it then try again')

        try:
            if enconding is None:
                outfile = open(micro_link_filepath, 'w', newline='', errors='ignore')
            else:
                outfile = open(micro_link_filepath, 'w', newline='', errors='ignore', encoding=enconding)

            write = csv.writer(outfile)
            write.writerow(
                ['name', 'link_id', 'main_link_id','osm_way_id', 'from_node_id', 'to_node_id', 'link_type_name',
                 'electrified', 'frequency', 'highspeed', 'free_speed','maxspeed_designed', 'passenger_lines',
                 'railway_ctcs','railway_traffic_mode', 'start_date', 'usage', 'voltage', 'gauge', 'service', 'length',
                 'lanes','capacity', 'geometry'])
            link_id = 0
            for link in network.micro_link_list:
                name = link.name if link.name else ''
                link_type_name = link.link_type_name if link.link_type_name else ''
                electrified = link.electrified if link.electrified else ''
                frequency = link.frequency if link.frequency else ''
                highspeed = link.highspeed if link.highspeed else ''
                free_speed = link.free_speed if link.free_speed else ''
                maxspeed_designed = link.maxspeed_designed if link.maxspeed_designed else ''
                passenger_lines = link.passenger_lines if link.passenger_lines else ''
                railway_ctcs = link.railway_ctcs if link.railway_ctcs else ''
                railway_traffic_mode = link.railway_traffic_mode if link.railway_traffic_mode else ''
                start_date = link.start_date if link.start_date else ''
                usage = link.usage if link.usage else ''
                voltage = link.voltage if link.voltage else ''
                gauge = link.gauge if link.gauge else ''
                service = link.service if link.service else ''
                lanes=1
                line = [name, link_id,link.main_link_id, link.osm_way_id, link.from_node.node_id, link.to_node.node_id,
                        link_type_name, electrified, frequency,highspeed, free_speed, maxspeed_designed,passenger_lines,
                        railway_ctcs, railway_traffic_mode, start_date, usage, voltage, gauge, service, link.length,lanes,
                        link.capacity,link.geometry.wkt]
                write.writerow(line)
                link_id += 1
            outfile.close()
        except PermissionError:
            print('micro link.csv may be locked by other programs. please release it then try again')
