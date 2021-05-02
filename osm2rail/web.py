import os
import sys
import time
import random
import requests
import fake_useragent



""" home page"""
def nominatim_homepage():
    return 'https://www.openstreetmap.org/api/0.6/map?bbox='
def xapi_homepage():
    return 'http://overpass.openstreetmap.ru/cgi/xapi_meta?*'
def overpass_homepage():
    return 'https://overpass-api.de/api/map?bbox='
def geofabrik_homepage():
    return 'http://download.geofabrik.de/'
def bbbike_homepage():
    return 'http://download.bbbike.org/osm/bbbike/'



""" make fake request headers"""
def fake_requests_headers(randomized=False):
    try:
        fake_user_agent = fake_useragent.UserAgent(verify_ssl=False)
        ua = fake_user_agent.random if randomized else fake_user_agent['google chrome']

    except fake_useragent.FakeUserAgentError:
        fake_user_agent = fake_useragent.UserAgent(verify_ssl=False)

        if randomized:
            ua = random.choice(fake_user_agent.data_browsers['internetexplorer'])
        else:
            ua = fake_user_agent['Internet Explorer']

    fake_headers = {'User-Agent': ua}

    return fake_headers


"""determine the coordinate range of target area"""
def get_subregion_download_range(area):
    html = requests.get(f'https://nominatim.openstreetmap.org/search?format=json&q={area}')
    if html.text=='[]':
        print('Unable to query the address,please try other keys')
        sys.exit(0)
    else:
        info = eval(html.text)[0]
        return info['boundingbox']

"""download .osm file for NominatimDownloader and OverpassDownloader"""
def download_osmfile_from_url(url, path_to_file,random_header=False, **kwargs):
    headers = fake_requests_headers(randomized=random_header)
    # Streaming, so we can iterate over the response
    resp = requests.get(url, stream=True, headers=headers)
    if resp.status_code == 429:
        print("\033[31m Error! Too many requests, please try again later, or try to use random header.[0m", end=" ")
    if resp.status_code==400:
        print(resp.text)
    total_size = resp.content.__sizeof__()-33 # Total size in bytes
    block_size = 1024*1024
    wrote = 0

    path_to_dir = os.path.dirname(path_to_file)
    if path_to_dir == "":
        path_to_file = os.path.join(os.getcwd(), path_to_file)
    else:
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)

    with open(path_to_file, mode='wb', **kwargs) as f:
        for data in resp.iter_content(block_size, decode_unicode=True):
            wrote = wrote + len(data)
            print("\033[31m \r download progress：%.2f MB(%.2f MB)\033[0m" % (wrote /block_size,total_size/block_size), end=" ")
            try:
                f.write(data)
            except TypeError:
                f.write(data.encode())
            time.sleep(0.5)
        f.close()
    resp.close()
    print()
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong!")


