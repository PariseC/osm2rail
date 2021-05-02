import re
import io
import bs4
import csv
import pandas as pd
from .utils import *
from .setting import *
from pyhelpers.dir import validate_input_data_dir
from pyhelpers.ops import confirmed, download_file_from_url, fake_requests_headers,update_nested_dict
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import find_similar_str


def get_list_of_cities(update=False, confirmation_required=True, verbose=False):
    path_to_pickle = cd_dat(BBBikeCitiesNames.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_pickle) and not update:
        cities_names = load_pickle(path_to_pickle)

    else:
        if confirmed("To collect {}?".format(BBBikeCitiesNames), confirmation_required=confirmation_required):

            try:
                cities_names_ = pd.read_csv(BBBikeURLCities, header=None)
                cities_names = list(cities_names_.values.flatten())

                save_pickle(cities_names, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                cities_names = None

        else:
            if verbose:
                print("No data of \"{}\" is available.".format(BBBikeCitiesNames))
            cities_names = None

    return cities_names

def get_coordinates_of_cities(update=False, confirmation_required=True, verbose=False):

    path_to_pickle = cd_dat(BBBikeCitiesCoordinates.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_pickle) and not update:
        cities_coordinates = load_pickle(path_to_pickle)

    else:
        if confirmed("To collect {}?".format(BBBikeCitiesCoordinates),
                     confirmation_required=confirmation_required):

            try:
                csv_temp = urllib.request.urlopen(BBBikeURLCitiesCoordinates)
                csv_file = list(csv.reader(io.StringIO(csv_temp.read().decode('utf-8')),delimiter=':'))

                csv_data = [[x.strip().strip('\u200e').replace('#', '') for x in row] for row in csv_file[5:-1]]
                column_names = [x.replace('#', '').strip().capitalize() for x in csv_file[0]]
                cities_coords = pd.DataFrame(csv_data, columns=column_names)

                coordinates = cities_coords.Coord.str.split(' ').apply(pd.Series)
                coords_cols = ['ll_longitude', 'll_latitude1','ur_longitude', 'ur_latitude']
                coordinates.columns = coords_cols

                cities_coords.drop(['Coord'], axis=1, inplace=True)

                cities_coordinates = pd.concat([cities_coords, coordinates], axis=1)

                cities_coordinates.dropna(subset=coords_cols, inplace=True)

                save_pickle(cities_coordinates, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                cities_coordinates = None

        else:
            if verbose:
                print("No data of \"{}\" is available.".format(BBBikeCitiesCoordinates))
            cities_coordinates = None

    return cities_coordinates

def get_subregion_catalogue(update=False, confirmation_required=True,verbose=False):

    path_to_pickle = cd_dat(BBBikeSubregionCatalogue.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_pickle) and not update:
        subregion_catalogue = load_pickle(path_to_pickle)

    else:
        if confirmed("To collect {}?".format(BBBikeSubregionCatalogue),confirmation_required=confirmation_required):

            try:
                bbbike_subregion_catalogue_ = pd.read_html(BBBikeURL, header=0, parse_dates=['Last Modified'])
                subregion_catalogue = bbbike_subregion_catalogue_[0].drop(0).drop(['Size', 'Type'], axis=1)
                subregion_catalogue.Name = subregion_catalogue.Name.map(lambda x: x.strip('/'))

                source = requests.get(BBBikeURL, headers=fake_requests_headers())
                table_soup = bs4.BeautifulSoup(source.text, 'lxml').find('table')
                urls = [urllib.parse.urljoin(BBBikeURL, x.get('href')) for x in table_soup.find_all('a')[1:]]

                subregion_catalogue['URL'] = urls

                save_pickle(subregion_catalogue, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                subregion_catalogue = None

        else:
            if verbose:
                print("No data of \"{}\" is available.".format(BBBikeSubregionCatalogue))
            subregion_catalogue = None

    return subregion_catalogue

def get_list_of_subregion_names(update=False, confirmation_required=True,verbose=False):

    path_to_name_list = cd_dat(BBBikeSubregionNameList.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_name_list) and not update:
        subregion_name_list = load_pickle(path_to_name_list)

    else:
        if confirmed("To get {}?".format(BBBikeSubregionNameList),confirmation_required=confirmation_required):

            subregion_catalogue = get_subregion_catalogue(update, confirmation_required=False, verbose=verbose)

            subregion_name_list = subregion_catalogue.Name.to_list()

            save_pickle(subregion_name_list, path_to_name_list, verbose=verbose)

        else:
            subregion_name_list = []
            if verbose:
                print("No data of {} is available.".format(BBBikeSubregionNameList))

    return subregion_name_list

def validate_input_subregion_name(subregion_name):

    assert isinstance(subregion_name, str)

    bbbike_subregion_names =get_list_of_subregion_names()

    subregion_name_ = find_similar_str(subregion_name, bbbike_subregion_names)

    return subregion_name_

def get_subregion_download_catalogue(subregion_name, confirmation_required=True,verbose=False):
    subregion_name_ = validate_input_subregion_name(subregion_name)

    if confirmed("Confirmed to collect the download catalogue for {}?".format(subregion_name_),
                 confirmation_required=confirmation_required):

        try:
            if confirmation_required:
                print("In progress", end=" ... ") if verbose else ""
            else:
                print(f" {subregion_name_}", end=" ... ") if verbose else ""

            url = urllib.parse.urljoin(BBBikeURL, subregion_name_ + '/')

            source = requests.get(url, headers=fake_requests_headers())

            source_soup = bs4.BeautifulSoup(source.text, 'lxml')
            download_links_class = source_soup.find_all(name='a', attrs={'class': ['download_link', 'small']})

            def parse_dlc(dlc):
                dlc_href = dlc.get('href')  # URL
                filename = os.path.basename(dlc_href)
                download_url = urllib.parse.urljoin(url, dlc_href)
                if not dlc.has_attr('title'):
                    file_format, file_size, last_update = 'Poly', None, None
                else:
                    if len(dlc.contents) < 3:
                        file_format, file_size = 'Txt', None
                    else:
                        file_format, file_size, _ = dlc.contents  # File type and size
                        file_format, file_size = file_format.strip(), file_size.text
                    last_update = pd.to_datetime(dlc.get('title'))  # Date and time
                parsed_dat = [filename, download_url, file_format, file_size, last_update]
                return parsed_dat

            subregion_download_catalogue = pd.DataFrame(parse_dlc(x) for x in download_links_class)
            subregion_download_catalogue.columns = ['Filename', 'URL', 'DataType', 'Size', 'LastUpdate']

            print("Done. ") if verbose else ""

        except Exception as e:
            subregion_download_catalogue = None
            print("Failed. {}".format(subregion_name_, e)) if verbose else ""

        return subregion_download_catalogue

def get_download_index(update=False, confirmation_required=True, verbose=False):

    path_to_pickle = cd_dat(BBBikeDownloadDictName.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_pickle) and not update:
        download_dictionary = load_pickle(path_to_pickle)

    else:
        if confirmed("To collect {} from BBBike's free download server?".format(
                BBBikeDownloadDictName), confirmation_required=confirmation_required):

            try:
                bbbike_subregion_names =get_subregion_catalogue(verbose=verbose).Name.to_list()

                if verbose:
                    print("Collecting {} ... ".format(BBBikeDownloadDictName))

                download_catalogue = [
                    get_subregion_download_catalogue(subregion_name,confirmation_required=False,verbose=verbose)
                    for subregion_name in bbbike_subregion_names]

                sr_name = bbbike_subregion_names[0]
                sr_download_catalogue = download_catalogue[0]

                # Available file formats
                file_fmt = [re.sub('{}|CHECKSUM'.format(sr_name), '', f) for f in sr_download_catalogue.Filename]

                # Available data types
                data_typ = sr_download_catalogue.DataType.tolist()

                download_dictionary = {'FileFormat': [x.replace(".osm", "", 1) for x in file_fmt[:-2]],
                                       'DataType': data_typ[:-2],
                                       'Catalogue':dict(zip(bbbike_subregion_names, download_catalogue))}

                print("Finished. ") if verbose else ""

                save_pickle(download_dictionary, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                download_dictionary = None

        else:
            if verbose:
                print("No data of \"{}\" is available.".format(BBBikeDownloadDictName))
            download_dictionary = None

    return download_dictionary


def get_osm_file_formats():

    osm_file_formats =get_download_index()['FileFormat']

    return osm_file_formats

def validate_input_file_format(osm_file_format):

    assert isinstance(osm_file_format, str)
    bbbike_osm_file_formats =get_osm_file_formats()

    try:
        osm_file_format_ = find_similar_str(osm_file_format, bbbike_osm_file_formats)

        if osm_file_format_:
            return osm_file_format_

        else:
            print("The input file format must be one of the following:"
                  " \n  \"{}\".".format("\",\n  \"".join(bbbike_osm_file_formats)))

    except Exception as e:
        print(e)

def get_subregion_download_url(subregion_name, osm_file_format):

    subregion_name_ = validate_input_subregion_name(subregion_name)
    osm_file_format_ = ".osm" + validate_input_file_format(osm_file_format)

    bbbike_download_dictionary = get_download_index()['Catalogue']
    sub_download_catalogue = bbbike_download_dictionary[subregion_name_]

    tmp = subregion_name_ + osm_file_format_
    url = sub_download_catalogue[sub_download_catalogue.Filename == tmp].URL.iloc[0]

    return subregion_name_, url

def get_valid_download_info(subregion_name, osm_file_format, download_dir=None):

    subregion_name_, download_url = get_subregion_download_url(subregion_name, osm_file_format)
    osm_filename = os.path.basename(download_url)

    if download_dir:
        path_to_file = cd(validate_input_data_dir(download_dir), osm_filename,
                          mkdir=True)
    else:
        # default directory of package data
        path_to_file = cd_dat_bbbike(subregion_name_, osm_filename, mkdir=True)

    return subregion_name_, osm_filename, download_url, path_to_file


def download_osm_data_from_bbbike(subregion_names, osm_file_format, download_dir='osmfile',update=False,
                      confirmation_required=True, interval_sec=10,verbose=False,random_header=False,
                      ret_download_path=False):

    subregion_names_ = [subregion_names] if isinstance(subregion_names, str) else subregion_names.copy()
    subregion_names_ = [validate_input_subregion_name(x) for x in subregion_names_]

    osm_file_format_ = validate_input_file_format(osm_file_format)

    download_path = []

    if confirmed("Confirmed to download {} data of the following geographic region(s):"
                 "\n\t{}\n?".format(osm_file_format_, "\n\t".join(subregion_names_)),
                 confirmation_required=confirmation_required):

        for sub_reg_name in subregion_names_:
            subregion_name_, osm_filename, download_url, path_to_file = \
                get_valid_download_info(sub_reg_name, osm_file_format_,download_dir)

            if os.path.isfile(path_to_file) and not update:
                if verbose:
                    print(
                        "The {} data of {} is already available at \"\\{}\".".format(
                            osm_file_format_, subregion_name_,
                            os.path.relpath(path_to_file)))

                download_path.append(path_to_file)

            else:
                try:
                    if verbose:
                        print("{} \"{}\" to \"\\{}\" ... ".format(
                            "Updating" if os.path.isfile(path_to_file)
                            else "Downloading",
                            osm_filename,
                            os.path.relpath(os.path.dirname(path_to_file))))

                    download_osmfile_from_url(url=download_url,path_to_file=path_to_file,random_header=random_header)

                    print("Done. ") if verbose else ""

                    download_path.append(path_to_file)

                    if os.path.getsize(path_to_file) / (1024 ** 2) <= 5:
                        time.sleep(interval_sec)

                except Exception as e:
                    print("Failed. {}.".format(e))

        if ret_download_path:
            if len(download_path) == 1:
                download_path = download_path[0]

            return download_path

def download_subregion_data_from_bbbike(subregion_name, download_dir='osmfile', update=False,confirmation_required=True,
                           verbose=False,random_header=False,ret_download_path=False):


    subregion_name_ = validate_input_subregion_name(subregion_name)
    bbbike_download_dictionary =get_download_index()['Catalogue']
    sub_download_catalogue = bbbike_download_dictionary[subregion_name_]

    data_dir = validate_input_data_dir(download_dir) if download_dir \
        else cd_dat_bbbike(subregion_name_, mkdir=True)

    if confirmed("Confirmed to download all available BBBike OSM data of {}?".format(
            subregion_name_), confirmation_required=confirmation_required):

        if verbose:
            if confirmation_required:
                print("Downloading in progress ... ")
            else:
                print("Downloading all available BBBike OSM data of {} ... ".format(
                    subregion_name_))

        download_paths = []

        for download_url, osm_filename in zip(sub_download_catalogue.URL,
                                              sub_download_catalogue.Filename):
            try:
                path_to_file = os.path.join(
                    data_dir, "" if not download_dir
                    else subregion_name_, osm_filename)

                if os.path.isfile(path_to_file) and not update:
                    if verbose:
                        print("\t\"{}\" is already available.".format(
                            os.path.basename(path_to_file)))

                else:
                    print("\t{} ... ".format(osm_filename)) if verbose else ""

                    download_osmfile_from_url(url=download_url, path_to_file=path_to_file,random_header=random_header)

                download_paths.append(path_to_file)

            except Exception as e:
                print("Failed. {}.".format(e))

        if verbose and download_paths:
            print("Done. Check out the downloaded OSM data at \"\\{}\".".format(
                os.path.relpath(os.path.dirname(download_paths[0]))))

        if ret_download_path:
            return download_paths