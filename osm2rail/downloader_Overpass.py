from .utils import *
from .web import *

def get_download_url(box):
    URL = overpass_homepage()
    min_lat, max_lat, min_lon, max_lon = box
    url = URL + str(min_lon) + ',' + str(min_lat) + ',' + str(max_lon) + ',' + str(max_lat)
    return url

def make_download_file(subarea_name, download_dir):
    path_to_file = os.path.join(download_dir, subarea_name) + '.osm'
    if os.path.isfile(path_to_file):
        print("\"{}\" is already available at \"\\{}\".".format(
            os.path.basename(path_to_file),
            os.path.relpath(os.path.dirname(path_to_file))))
        return True,path_to_file
    return False,path_to_file

def download_osm_data_from_overpass(subarea_names=None,boxs=None,download_dir='osmfile',interval_sec=10,random_header=False,
                      ret_download_path=False):

    download_dir_ = validate_download_dir(download_dir)

    download_paths = []

    if subarea_names:

        subarea_names_ = [subarea_names] if isinstance(subarea_names, str) else subarea_names.copy()

        for subarea_name in subarea_names_:
            subarea_name_=subarea_name.replace(' ','_')
            is_downloaded,path_to_file = make_download_file(subarea_name_, download_dir_)
            download_paths.append(path_to_file)
            if not is_downloaded:
                print("Downloading \"{}.osm\" to \"\\{}\"...".format(subarea_name_,os.path.relpath(os.path.dirname(path_to_file))))
                box = get_subregion_download_range(subarea_name)
                if box:
                    url = get_download_url(box)
                    try:
                        download_osmfile_from_url(url=url,path_to_file=path_to_file,random_header=random_header)
                        print('Done.')
                    except Exception as e:
                        print("Failed. {}.".format(e))
                    if interval_sec and len(subarea_names_)>1:
                        time.sleep(interval_sec)
    if boxs:
        boxs_ = [boxs] if isinstance(boxs, tuple) else boxs.copy()
        for id,box in enumerate(boxs_):
            subbox_name='map_'+str(id+1)
            is_downloaded,path_to_file = make_download_file(subbox_name, download_dir_)
            download_paths.append(path_to_file)
            if not is_downloaded:
                print("Downloading \"{}.osm\" to \"\\{}\"...".format(subbox_name,os.path.relpath(os.path.dirname(path_to_file))))
                try:
                    url = get_download_url(box)
                    download_osmfile_from_url(url=url,path_to_file=path_to_file,random_header=random_header)
                    print('Done.')
                except Exception as e:
                    print("Failed. {}.".format(e))
            if interval_sec and len(boxs_)>1:
                time.sleep(interval_sec)
    if ret_download_path:
        return download_paths
