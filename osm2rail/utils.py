import math
import os
import pkg_resources
import re
import copy
import pathlib
import string
import fuzzywuzzy.fuzz
import difflib
import pickle
import collections
import numpy as np

def update_nested_dict(source_dict, updates):
    for key, val in updates.items():
        if isinstance(val, collections.abc.Mapping) or isinstance(val, dict):
            source_dict[key] = update_nested_dict(source_dict.get(key, {}), val)

        elif isinstance(val, list):
            source_dict[key] = (source_dict.get(key, []) + val)

        else:
            source_dict[key] = updates[key]

    return source_dict

def remove_punctuation(raw_txt, rm_whitespace=False):

    try:
        txt = raw_txt.translate(str.maketrans('', '', string.punctuation))

    except Exception as e:
        print(e)
        txt = ''.join(x for x in raw_txt if x not in string.punctuation)

    if rm_whitespace:
        txt = ' '.join(txt.split())

    return txt

def find_similar_str(str_x, lookup_list, n=1, processor='fuzzywuzzy', ignore_punctuation=True,
                     **kwargs):
    assert processor in ('difflib', 'fuzzywuzzy'), \
        "Options for `processor` include \"difflib\" and \"fuzzywuzzy\"."

    n_ = len(lookup_list) if n is None else n

    if processor == 'fuzzywuzzy':

        l_distances = [fuzzywuzzy.fuzz.token_set_ratio(str_x, a, **kwargs) for a in lookup_list]

        if sum(l_distances) == 0:
            sim_str = None
        else:
            if n_ == 1:
                sim_str = lookup_list[l_distances.index(max(l_distances))]
            else:
                sim_str = [lookup_list[i] for i in np.argsort(l_distances)[::-1]][:n_]

    elif processor == 'difflib':
        if not ignore_punctuation:
            str_x_ = str_x.lower()
            lookup_list_ = {x_.lower(): x_ for x_ in lookup_list}
        else:
            str_x_ = remove_punctuation(str_x.lower())
            lookup_list_ = {remove_punctuation(x_.lower()): x_ for x_ in lookup_list}

        sim_str_ = difflib.get_close_matches(str_x_, lookup_list_.keys(), n=n_, **kwargs)

        if not sim_str_:
            sim_str = None
        else:
            sim_str = lookup_list_[sim_str_[0]]

    else:
        sim_str = None

    return sim_str

def _get_specific_filepath_info(path_to_file, verbose=False, verbose_end=" ... ", ret_info=False):

    abs_path_to_file = pathlib.Path(path_to_file).absolute()
    assert not abs_path_to_file.is_dir(), "The input for `path_to_file` may not be a file path."

    filename = pathlib.Path(abs_path_to_file).name if abs_path_to_file.suffix else ""

    try:
        rel_path = pathlib.Path(os.path.relpath(abs_path_to_file.parent))

        if rel_path == rel_path.parent:
            rel_path = abs_path_to_file.parent
            msg_fmt = "{} \"{}\""
        else:
            msg_fmt = "{} \"{}\" {} \"{}\\\""
            # The specified path exists?
            os.makedirs(abs_path_to_file.parent, exist_ok=True)

    except ValueError:
        if verbose == 2:
            warn_msg = "Warning: \"{}\" is outside the current working directory".format(
                str(abs_path_to_file.parent))
            print(warn_msg)

        rel_path = abs_path_to_file.parent
        msg_fmt = "{} \"{}\""

    if verbose:
        if os.path.isfile(abs_path_to_file):
            status_msg, prep = "Updating", "at"
        else:
            status_msg, prep = "Saving", "to"

        if verbose_end:
            verbose_end_ = verbose_end
        else:
            verbose_end_ = "\n"

        if rel_path == rel_path.parent:
            print(msg_fmt.format(status_msg, filename), end=verbose_end_)
        else:
            print(msg_fmt.format(status_msg, filename, prep, rel_path), end=verbose_end_)

    if ret_info:
        return rel_path, filename

def save_pickle(pickle_data, path_to_pickle, mode='wb', verbose=False, **kwargs):

    _get_specific_filepath_info(path_to_pickle, verbose=verbose, ret_info=False)

    try:
        pickle_out = open(path_to_pickle, mode=mode)
        pickle.dump(pickle_data, pickle_out, **kwargs)
        pickle_out.close()
        print("Done.") if verbose else ""

    except Exception as e:
        print("Failed. {}.".format(e))

def load_pickle(path_to_pickle, mode='rb', verbose=False, **kwargs):

    if verbose:
        print("Loading \"{}\"".format(os.path.relpath(path_to_pickle)), end=" ... ")

    try:
        pickle_in = open(path_to_pickle, mode=mode)
        pickle_data = pickle.load(pickle_in, **kwargs)
        pickle_in.close()
        print("Done.") if verbose else ""
        return pickle_data

    except Exception as e:
        print("Failed. {}".format(e)) if verbose else ""

def confirmed(prompt=None, confirmation_required=True, resp=False):

    if confirmation_required:
        if prompt is None:
            prompt_ = "Confirmed? "
        else:
            prompt_ = copy.copy(prompt)

        if resp is True:  # meaning that default response is True
            prompt_ = "{} [{}]|{}: ".format(prompt_, "Yes", "No")
        else:
            prompt_ = "{} [{}]|{}: ".format(prompt_, "No", "Yes")

        ans = input(prompt_)
        if not ans:
            return resp

        if re.match('[Yy](es)?', ans):
            return True
        if re.match('[Nn](o)?', ans):
            return False

    else:
        return True

def validate_input_data_dir(input_data_dir=None, msg="Invalid input!", sub_dir=""):
    if input_data_dir:
        assert isinstance(input_data_dir, str), msg

        if not os.path.isabs(input_data_dir):  # Use default file directory
            data_dir_ = cd(input_data_dir.strip('.\\.'))

        else:
            data_dir_ = os.path.realpath(input_data_dir.lstrip('.\\.'))
            assert os.path.isabs(input_data_dir), msg

    else:
        data_dir_ = cd(sub_dir) if sub_dir else cd()

    return data_dir_

def cd(*sub_dir, mkdir=False, cwd=None, back_check=False, **kwargs):
    # Current working directory
    path = os.getcwd() if cwd is None else copy.copy(cwd)

    if back_check:
        while not os.path.exists(path):
            path = os.path.dirname(path)

    for x in sub_dir:
        path = os.path.dirname(path) if x == ".." else os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)

        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path

def cd_dat(*sub_dir, dat_dir="dat", mkdir=False, **kwargs):
    path = pkg_resources.resource_filename(__name__, dat_dir)

    for x in sub_dir:
        path = os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)

        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path

def cd_dat_geofabrik(*sub_dir, mkdir=False, **kwargs):

    path = cd("dat_Geofabrik", *sub_dir, mkdir=mkdir, **kwargs)

    return path

def cd_dat_bbbike(*sub_dir, mkdir=False, **kwargs):

    path = cd("dat_BBBike", *sub_dir, mkdir=mkdir, **kwargs)

    return path

def get_distance_from_coord(lon1, lat1, lon2, lat2):
    # return km
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371
    return c * r

def validate_download_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return dirname