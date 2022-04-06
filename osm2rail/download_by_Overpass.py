from .utils import *
from .web import *

def _get_download_url(box):
    url_ = overpass_homepage()
    min_lat, max_lat, min_lon, max_lon = box
    url = url_ + str(min_lon) + ',' + str(min_lat) + ',' + str(max_lon) + ',' + str(max_lat)
    return url

def _make_download_file(subarea_name, download_dir):
    path_to_file = os.path.join(download_dir, subarea_name) + '.osm'
    if os.path.isfile(path_to_file):
        print("\"{}\" is already available at \"\\{}\".".format(
            os.path.basename(path_to_file),
            os.path.relpath(os.path.dirname(path_to_file))))
        return True,path_to_file
    return False,path_to_file

def download_osm_data_from_overpass(subarea_names=None,bboxs=None,download_dir='osmfile',
                               interval_sec=10,ret_download_path=False):
    """
    :param subarea_names: str or list,the names of the subarea to be downloaded.
    :param bboxs: tuple(min_lat, max_lat,min_lon, max_lon).
    :param download_dir: str, the path to save the downloaded files.
    :param interval_sec: float,
    :param ret_download_path:
    :return:
    """

    download_dir_ = validate_download_dir(download_dir)
    download_paths = []

    if subarea_names:
        if isinstance(subarea_names,str):
            subarea_names_=[subarea_names]
        elif isinstance(subarea_names,list):
            subarea_names_=subarea_names
        else:
            subarea_names_=[]
            print(" 'subarea_names' should be valued by str or list ")

        for subarea_name in subarea_names_:
            subarea_name_=subarea_name.replace(' ','_')
            is_downloaded,osm_filename = _make_download_file(subarea_name_, download_dir_)
            download_paths.append(osm_filename)
            if not is_downloaded:
                box = get_subregion_download_range(subarea_name)
                print("The box of {} is {} ".format(subarea_name_,box))
                print("Downloading \"{}.osm\" to \"\\{}\"...".format(subarea_name_,os.path.relpath(os.path.dirname(osm_filename))),end='')
                if box:
                    url = _get_download_url(box)
                    try:
                        download_osmfile_from_url(url=url,osm_filename=osm_filename)
                        print('Done.')
                    except Exception as e:
                        print("Failed. {}.".format(e))
                    if interval_sec and len(subarea_names_)>1:
                        time.sleep(interval_sec)
    if bboxs:
        if isinstance(bboxs,tuple):
            bboxs_=[bboxs]
        elif isinstance(bboxs,list):
            bboxs_=bboxs
        else:
            bboxs_=[]
            print(" 'bboxs' should be valued by tuple or list ")

        for id,box in enumerate(bboxs_):
            subbox_name='map_'+str(id+1)
            is_downloaded,osm_filename = _make_download_file(subbox_name, download_dir_)
            download_paths.append(osm_filename)
            if not is_downloaded:
                print("Downloading \"{}.osm\" to \"\\{}\"...".format(subbox_name,os.path.relpath(os.path.dirname(osm_filename))))
                try:
                    url = _get_download_url(box)
                    download_osmfile_from_url(url=url,osm_filename=osm_filename)
                    print('Done.')
                except Exception as e:
                    print("Failed. {}.".format(e))
            if interval_sec and len(bboxs_)>1:
                time.sleep(interval_sec)
    if ret_download_path:
        return download_paths
