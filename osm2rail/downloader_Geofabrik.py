import re
import bs4
import copy
import pandas as pd
import numpy as np
from .utils import *
from .setting import *
from pyhelpers.dir import validate_input_data_dir
from pyhelpers.ops import confirmed,  fake_requests_headers,update_nested_dict
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import find_similar_str


def get_raw_directory_index(url, verbose=False):
    try:
        import humanfriendly

        raw_directory_index = pd.read_html(url, match='file', header=0, parse_dates=['date'])
        raw_directory_index = pd.concat(raw_directory_index, ignore_index=True)
        raw_directory_index.columns = [c.title() for c in raw_directory_index.columns]

        # Clean the DataFrame
        raw_directory_index.Size = raw_directory_index.Size.apply(humanfriendly.format_size)
        raw_directory_index.sort_values('Date', ascending=False, inplace=True)
        raw_directory_index.index = range(len(raw_directory_index))

        raw_directory_index['FileURL'] = raw_directory_index.File.map(
            lambda x: urllib.parse.urljoin(url, x))

    except (urllib.error.HTTPError, TypeError, ValueError):
        if len(urllib.parse.urlparse(url).path) <= 1 and verbose:
            print("The web page does not have a raw directory index.")
        raw_directory_index = None

    return raw_directory_index

def get_subregion_table(url, verbose=False):

        try:
            subregion_table = pd.read_html(
                url, match=re.compile(r'(Special )?Sub[ \-]Regions?'), encoding='UTF-8')
            subregion_table = pd.concat(subregion_table, axis=0, ignore_index=True)

            # Specify column names
            file_formats = GeofabrikValidFileFormats
            column_names = ['Subregion'] + file_formats
            column_names.insert(2, '.osm.pbf.Size')

            # Add column/names
            if len(subregion_table.columns) == 4:
                subregion_table.insert(2, '.osm.pbf.Size', np.nan)
            subregion_table.columns = column_names

            subregion_table.replace(
                {'.osm.pbf.Size': {re.compile('[()]'): '', re.compile('\xa0'): ' '}},
                inplace=True)

            # Get the URLs
            source = requests.get(url, headers=fake_requests_headers())
            soup = bs4.BeautifulSoup(source.content, 'lxml')
            source.close()

            for file_type in file_formats:
                text = '[{}]'.format(file_type)
                urls = [urllib.parse.urljoin(url, link['href']) for link in
                        soup.find_all(name='a', href=True, text=text)]
                subregion_table.loc[
                    subregion_table[file_type].notnull(), file_type] = urls

            try:
                subregion_urls = [
                    urllib.parse.urljoin(url, soup.find('a', text=text).get('href'))
                    for text in subregion_table.Subregion]
            except (AttributeError, TypeError):
                subregion_urls = [kml['onmouseover']
                                  for kml in soup.find_all('tr', onmouseover=True)]
                subregion_urls = [
                    s[s.find('(') + 1:s.find(')')][1:-1].replace('kml', 'html')
                    for s in subregion_urls]
                subregion_urls = [urllib.parse.urljoin(url, sub_url)
                                  for sub_url in subregion_urls]
            subregion_table['SubregionURL'] = subregion_urls

            column_names = list(subregion_table.columns)
            column_names.insert(1, column_names.pop(len(column_names) - 1))
            subregion_table = subregion_table[column_names]

            subregion_table['.osm.pbf.Size'] = \
                subregion_table['.osm.pbf.Size'].str.replace('(', '').str.replace(')', '')

            subregion_table = subregion_table.where(pd.notnull(subregion_table), None)

        except (ValueError, TypeError, ConnectionRefusedError, ConnectionError):
            # No more data available for subregions within the region
            if verbose:
                print("Checked out \"{}\".".format(
                    url.split('/')[-1].split('.')[0].title()))
            subregion_table = None

        return subregion_table

def get_download_index(update=False, confirmation_required=True, verbose=False):
    path_to_download_index = cd_dat(GeofabrikDownloadIndexName.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_download_index) and not update:
        download_index = load_pickle(path_to_download_index)

    else:
        if confirmed("To get {}?".format(GeofabrikDownloadIndexName),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting {}".format(GeofabrikDownloadIndexName), end=" ... ")
            try:
                import geopandas as gpd

                download_index_ = gpd.read_file(GeofabrikDownloadIndexURL)

                # Note that '<br />' exists in all the names of Poland' subregions
                download_index_.name = download_index_.name.str.replace('<br />', ' ')

                urls = download_index_.urls.map(
                    lambda x: pd.DataFrame.from_dict(x, 'index').T)
                urls_ = pd.concat(urls.values, ignore_index=True)
                download_index = pd.concat([download_index_, urls_], axis=1)

                print("Done. ") if verbose == 2 else ""

                save_pickle(download_index, path_to_download_index, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                download_index = None

        else:
            download_index = None
            if verbose:
                print("No data of {} is available.".format(GeofabrikDownloadIndexName))

    return download_index

def get_continents_subregion_tables(update=False, confirmation_required=True, verbose=False):
    path_to_pickle =cd_dat(GeofabrikContinentSubregionTableName.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_pickle) and not update:
        subregion_tables = load_pickle(path_to_pickle)

    else:
        if confirmed("To collect information of {}?".format(
                GeofabrikContinentSubregionTableName),
                confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting a table of {}".format(
                    GeofabrikContinentSubregionTableName), end=" ... ")

            try:
                # Scan the homepage to collect info of regions for each continent
                source = requests.get(GeofabrikURL, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml').find_all(
                    'td', {'class': 'subregion'})
                source.close()
                continent_names = [td.a.text for td in soup]
                continent_links = [urllib.parse.urljoin(GeofabrikURL, td.a['href'])
                                   for td in soup]
                subregion_tables = dict(
                    zip(continent_names,
                        [get_subregion_table(url, verbose)
                         for url in continent_links]))

                print("Done. ") if verbose == 2 else ""

                save_pickle(subregion_tables, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                subregion_tables = None

        else:
            subregion_tables = None
            if verbose:
                print(f"No data of {GeofabrikContinentSubregionTableName} is available.")

    return subregion_tables

def get_region_subregion_tier(update=False, confirmation_required=True,verbose=False):

    path_to_file = cd_dat(GeofabrikRegionSubregionTier.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        region_subregion_tier, non_subregions = load_pickle(path_to_file, verbose=verbose)
    else:
        def compile_region_subregion_tier(sub_reg_tbls):

            having_subregions = sub_reg_tbls.copy()
            region_subregion_tiers = having_subregions.copy()

            non_subregions_list = []
            for k, v in sub_reg_tbls.items():
                if v is not None and isinstance(v, pd.DataFrame):
                    region_subregion_tiers =update_nested_dict(sub_reg_tbls, {k: set(v.Subregion)})
                else:
                    non_subregions_list.append(k)

            for x in non_subregions_list:
                having_subregions.pop(x)

            having_subregions_temp = copy.deepcopy(having_subregions)

            while having_subregions_temp:
                for region_name, subregion_table in having_subregions.items():
                    subregion_names = subregion_table.Subregion
                    subregion_links = subregion_table.SubregionURL
                    sub_subregion_tables = dict(
                        zip(subregion_names,
                            [get_subregion_table(link)
                             for link in subregion_links]))

                    subregion_index, without_subregion_ =compile_region_subregion_tier(sub_subregion_tables)
                    non_subregions_list += without_subregion_

                    region_subregion_tiers.update({region_name: subregion_index})

                    having_subregions_temp.pop(region_name)

            # Russian Federation in both pages of Asia and Europe,
            # so there are duplicates in non_subregions_list
            import more_itertools

            non_subregions_list = list(more_itertools.unique_everseen(non_subregions_list))

            return region_subregion_tiers, non_subregions_list

        if confirmed("To compile {}? (Note this may take up to a few minutes.)".format(GeofabrikRegionSubregionTier),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Compiling {} ... ".format(GeofabrikRegionSubregionTier), end="")

            # Scan the download pages to collect a catalogue of region-subregion tier
            try:
                subregion_tables =get_continents_subregion_tables(update=update)
                region_subregion_tier, non_subregions = compile_region_subregion_tier(subregion_tables)

                print("Done. ") if verbose == 2 else ""

                save_pickle((region_subregion_tier, non_subregions), path_to_file,
                            verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                region_subregion_tier, non_subregions = None, None

        else:
            region_subregion_tier, non_subregions = None, None
            if verbose:
                print("No data of {} is available.".format(GeofabrikRegionSubregionTier))

    return region_subregion_tier, non_subregions

def get_download_catalogue(update=False, confirmation_required=True, verbose=False):

    path_to_downloads_catalogue = cd_dat(GeofabrikDownloadsCatalogue.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_downloads_catalogue) and not update:
        subregion_downloads_catalogue = load_pickle(path_to_downloads_catalogue)

    else:
        if confirmed("To collect {}? (Note that it may take a few minutes.)".format(GeofabrikDownloadsCatalogue),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting {}".format(GeofabrikDownloadsCatalogue), end=" ... ")
            try:
                source = requests.get(GeofabrikURL, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')
                source.close()

                subregion_href = soup.find_all('td', {'class': 'subregion'})
                avail_subregion_urls = (urllib.parse.urljoin(GeofabrikURL, td.a['href'])
                                        for td in subregion_href)
                avail_subregion_url_tables_0 = (get_subregion_table(sub_url, verbose)
                                                for sub_url in avail_subregion_urls)
                avail_subregion_url_tables = [tbl for tbl in avail_subregion_url_tables_0 if tbl is not None]

                subregion_url_tables = list(avail_subregion_url_tables)

                while subregion_url_tables:

                    subregion_url_tables_ = []

                    for subregion_url_table in subregion_url_tables:
                        subregion_urls = list(subregion_url_table.SubregionURL)
                        subregion_url_tables_0 = [
                            get_subregion_table(sr_url, verbose)
                            for sr_url in subregion_urls]
                        subregion_url_tables_ += [
                            tbl for tbl in subregion_url_tables_0 if tbl is not None]

                        avail_subregion_url_tables += subregion_url_tables_

                    subregion_url_tables = list(subregion_url_tables_)

                # All available URLs for downloading
                home_subregion_url_table = get_subregion_table(GeofabrikURL)
                avail_subregion_url_tables.append(home_subregion_url_table)
                subregion_downloads_catalogue = pd.concat(avail_subregion_url_tables,
                                                          ignore_index=True)
                subregion_downloads_catalogue.drop_duplicates(inplace=True)

                duplicated = subregion_downloads_catalogue[subregion_downloads_catalogue.Subregion.duplicated(keep=False)]
                if not duplicated.empty:
                    import humanfriendly

                    for i in range(0, 2, len(duplicated)):
                        temp = duplicated.iloc[i:i + 2]
                        size = temp['.osm.pbf.Size'].map(lambda x: humanfriendly.parse_size(
                            x.strip('(').strip(')').replace('\xa0', ' ')))
                        idx = size[size == size.min()].index
                        subregion_downloads_catalogue.drop(idx, inplace=True)
                    subregion_downloads_catalogue.index = range(len(subregion_downloads_catalogue))

                # Save subregion_index_downloads to local disk
                save_pickle(subregion_downloads_catalogue,
                            path_to_downloads_catalogue, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                subregion_downloads_catalogue = None

        else:
            subregion_downloads_catalogue = None
            if verbose:
                print("No data of {} is available.".format(GeofabrikDownloadsCatalogue))

    return subregion_downloads_catalogue

def get_list_of_subregion_names(update=False, confirmation_required=True,verbose=False):

    path_to_name_list = cd_dat(GeofabrikSubregionNameList.replace(" ", "-") + ".pickle")

    if os.path.isfile(path_to_name_list) and not update:
        subregion_name_list = load_pickle(path_to_name_list)

    else:
        if confirmed("To get {}?".format(GeofabrikSubregionNameList),confirmation_required=confirmation_required):

            downloads_catalogue = get_download_catalogue(update=update, confirmation_required=False)

            subregion_name_list = downloads_catalogue.Subregion.to_list()

            save_pickle(subregion_name_list, path_to_name_list, verbose=verbose)
        else:
            subregion_name_list = []
            if verbose:
                print("No data of {} is available.".format(GeofabrikSubregionNameList))
    return subregion_name_list

def validate_input_subregion_name(subregion_name):

    assert isinstance(subregion_name, str)
    # Get a list of available
    subregion_names = get_list_of_subregion_names()

    if os.path.isdir(os.path.dirname(subregion_name)) or urllib.parse.urlparse(subregion_name).path:
        subregion_name_ = find_similar_str(os.path.basename(subregion_name),
                                           subregion_names)
    else:
        subregion_name_ = find_similar_str(subregion_name, subregion_names)

    if not subregion_name_:
        raise ValueError(
            "The input subregion name is not identified.\n"
            "Check if the required subregion exists in the catalogue and retry.")

    return subregion_name_

def validate_input_file_format(osm_file_format):

    osm_file_format_ = find_similar_str(osm_file_format,GeofabrikValidFileFormats)

    assert osm_file_format_ in GeofabrikValidFileFormats,"The input file format must be one from {}.".format(
        GeofabrikValidFileFormats
    )

    return osm_file_format_


def get_subregion_download_url(subregion_name, osm_file_format, update=False,verbose=False):

    # Get an index of download URLs
    subregion_downloads_index =get_download_catalogue(update=update, verbose=verbose)
    subregion_downloads_index.set_index('Subregion', inplace=True)

    subregion_name_ = validate_input_subregion_name(subregion_name)
    osm_file_format_ = validate_input_file_format(osm_file_format)

    # Get the URL
    download_url = subregion_downloads_index.loc[subregion_name_, osm_file_format_]

    return subregion_name_, download_url

def get_default_osm_filename(subregion_name, osm_file_format, update=False):

    subregion_name_ = validate_input_subregion_name(subregion_name)
    osm_file_format_ =validate_input_file_format(osm_file_format)

    _, download_url = get_subregion_download_url(
        subregion_name_, osm_file_format_, update=update)

    if download_url is None:
        print("No {} data is available to download for {}.".format(
            osm_file_format_, subregion_name_))

    else:
        subregion_filename = os.path.split(download_url)[-1]
        return subregion_filename

def get_default_path_to_osm_file(subregion_name, osm_file_format, mkdir=False,update=False, verbose=False):

    subregion_name_ = validate_input_subregion_name(subregion_name)
    osm_file_format_ = validate_input_file_format(osm_file_format)

    subregion_name_, download_url = get_subregion_download_url(
        subregion_name_, osm_file_format_, update=update)

    if download_url is None:
        if verbose:
            print("{} data is not available for {}".format(
                osm_file_format_, subregion_name_))

        default_filename, default_file_path = None, None

    else:
        parsed_path = urllib.parse.urlparse(download_url).path.lstrip('/').split('/')

        if len(parsed_path) == 1:
            parsed_path = [subregion_name_] + parsed_path

        subregion_names = get_list_of_subregion_names()
        directory = cd_dat_geofabrik(*[find_similar_str(x, subregion_names) if x != 'us' else 'United States'
                                       for x in parsed_path[0:-1]],
                                     mkdir=mkdir)

        default_filename = parsed_path[-1]
        default_file_path = os.path.join(directory, default_filename)

    return default_filename, default_file_path

def search_for_subregions( *subregion_name, deep=False):

    region_subregion_tier, non_subregions_list = get_region_subregion_tier()

    if not subregion_name:
        subregion_names = non_subregions_list

    else:

        def find_subregions(reg_name, reg_sub_idx):

            for k, v in reg_sub_idx.items():
                if reg_name == k:
                    if isinstance(v, dict):
                        yield list(v.keys())
                    else:
                        yield [reg_name] if isinstance(reg_name, str) else reg_name
                elif isinstance(v, dict):
                    for sub in find_subregions(reg_name, v):
                        if isinstance(sub, dict):
                            yield list(sub.keys())
                        else:
                            yield [sub] if isinstance(sub, str) else sub

        res = []
        for region in subregion_name:
            res += list(find_subregions(validate_input_subregion_name(region),region_subregion_tier))[0]

        if not deep:
            subregion_names = res
        else:
            check_list = [x for x in res if x not in non_subregions_list]
            if check_list:
                res_ = list(set(res) - set(check_list))
                res_ += search_for_subregions(*check_list)
            else:
                res_ = res
            del non_subregions_list, region_subregion_tier, check_list

            subregion_names = list(dict.fromkeys(res_))

    return subregion_names

def make_sub_download_dir(subregion_name, osm_file_format, download_dir=None, mkdir=False):

    subregion_name_ =validate_input_subregion_name(subregion_name)
    osm_file_format_ =validate_input_file_format(osm_file_format)

    default_filename, default_file_path = get_default_path_to_osm_file(
        subregion_name_, osm_file_format_)

    if not default_filename:
        default_sub_dir = re.sub( r"[. ]", "-", subregion_name_.lower() + osm_file_format_)
    else:
        default_sub_dir = re.sub(r"[. ]", "-", default_filename).lower()

    if not download_dir:
        default_download_dir = cd_dat_geofabrik(os.path.dirname(default_file_path),default_sub_dir, mkdir=mkdir)

    else:
        default_download_dir = cd(validate_input_data_dir(download_dir),default_sub_dir, mkdir=mkdir)

    return default_download_dir

def osm_file_exists(subregion_name, osm_file_format, data_dir=None,update=False,verbose=False, ret_file_path=False):
    subregion_name_ = validate_input_subregion_name(subregion_name)
    osm_file_format_ =validate_input_file_format(osm_file_format)

    default_filename, path_to_file = get_default_path_to_osm_file(
        subregion_name_, osm_file_format_)

    if data_dir:
        path_to_file = cd(validate_input_data_dir(data_dir), default_filename)

    if os.path.isfile(path_to_file) and not update:
        if verbose == 2:
            print("\"{}\" of {} is available at \"{}\".".format(
                default_filename, subregion_name_,
                os.path.relpath(os.path.dirname(path_to_file))))

        if ret_file_path:
            return path_to_file
        else:
            return True
    else:
        return False


def download_osm_data_from_geofabrik(subregion_names, osm_file_format, download_dir='osmfile',update=False,
                      confirmation_required=False, deep_retry=False,interval_sec=10, verbose=False,
                      random_header=False,ret_download_path=False):

    subregion_names_ = [subregion_names] if isinstance(subregion_names, str) else subregion_names.copy()
    subregion_names_ = [validate_input_subregion_name(x) for x in subregion_names_]

    osm_file_format_ = validate_input_file_format(osm_file_format)

    if confirmed(
            "Confirmed to download {} data of the following geographic region(s):"
            "\n\t{}\n?".format(osm_file_format_, "\n\t".join(subregion_names_)),
            confirmation_required=confirmation_required):

        download_paths = []

        for sub_reg_name in subregion_names_:

            # Get download URL
            subregion_name_, download_url = get_subregion_download_url(
                sub_reg_name, osm_file_format_)

            if download_url is None:

                if verbose:
                    print("The {} data is not found for \"{}\".".format(
                        osm_file_format_, subregion_name_))

                if confirmed("Try downloading the data of its subregions instead",
                             confirmation_required=confirmation_required):

                    sub_subregions = search_for_subregions(
                        subregion_name_, deep=deep_retry)

                    if sub_subregions == [subregion_name_]:
                        print("No {} data is available "
                              "for this geographic region.".format(osm_file_format_))
                        break

                    else:
                        if not download_dir:
                            _, path_to_file_ = get_default_path_to_osm_file(
                                subregion_name_, ".osm.pbf")
                            download_dir = os.path.dirname(path_to_file_)

                        download_dir_ = make_sub_download_dir(
                            subregion_name_, osm_file_format_, download_dir)

                        download_osm_data_from_geofabrik(
                            sub_subregions, osm_file_format=osm_file_format_,
                            download_dir=download_dir_, update=update,
                            confirmation_required=False, verbose=verbose,
                            ret_download_path=ret_download_path)

            else:
                if not download_dir:
                    # Download the requested OSM file to default directory
                    osm_filename, path_to_file = get_default_path_to_osm_file(
                        subregion_name_, osm_file_format_, mkdir=True)
                else:
                    download_dir_ = validate_input_data_dir(download_dir)
                    osm_filename = get_default_osm_filename(
                        subregion_name_, osm_file_format=osm_file_format_)
                    path_to_file = os.path.join(download_dir_, osm_filename)

                download_paths.append(path_to_file)

                if os.path.isfile(path_to_file) and not update:
                    if verbose:
                        print("\"{}\" is already available at \"\\{}\".".format(
                            os.path.basename(path_to_file),
                            os.path.relpath(os.path.dirname(path_to_file))))

                else:
                    if verbose:
                        print("{} \"{}\" to \"\\{}\" ... ".format(
                            "Updating" if os.path.isfile(path_to_file)
                            else "Downloading",
                            osm_filename,
                            os.path.relpath(os.path.dirname(path_to_file))))

                    try:
                        download_osmfile_from_url(url=download_url, path_to_file=path_to_file,random_header=random_header)
                        print("Done. ") if verbose else ""
                    except Exception as e:
                        print("Failed. {}.".format(e))

            if len(subregion_names_)>1 and interval_sec:
                time.sleep(interval_sec)

        if ret_download_path:
            if len(download_paths) == 1:
                download_paths = download_paths[0]

            return download_paths

def download_subregion_data_from_geofabrik(subregion_names, osm_file_format, download_dir=None, update=False,verbose=False,
                            random_header=False,ret_download_path=False):

    subregion_names_ = [subregion_names] if isinstance(subregion_names, str) else subregion_names.copy()
    subregion_names_ = [validate_input_subregion_name(x) for x in subregion_names_]
    subregion_names_ = search_for_subregions(*subregion_names_)

    subregion_name_list = subregion_names_.copy()

    osm_file_format_ = validate_input_file_format(osm_file_format)

    for subregion_name in subregion_names_:
        if osm_file_exists(subregion_name, osm_file_format_, download_dir, update):
            subregion_name_list.remove(subregion_name)

    confirmation_required_ = False if not subregion_name_list else True

    if confirmed(
            "Confirmed to download {} data of the following geographic region(s): "
            "\n\t{}\n?".format(osm_file_format_, "\n\t".join(subregion_name_list)),
            confirmation_required=confirmation_required_):

        download_paths = download_osm_data_from_geofabrik(
            subregion_names_, osm_file_format=osm_file_format_,
            download_dir=download_dir, update=update, confirmation_required=False,
            verbose=verbose,random_header=random_header, ret_download_path=ret_download_path)

        if ret_download_path:
            if len(download_paths) == 1:
                download_paths = download_paths[0]
            return download_paths