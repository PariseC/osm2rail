import random
import requests
import sys
import time

def overpass_homepage():
    return 'https://overpass-api.de/api/map?bbox='
def geofabrik_homepage():
    return 'http://download.geofabrik.de/'
def bbbike_homepage():
    return 'http://download.bbbike.org/osm/bbbike/'

def fake_requests_headers():
    UA = [
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]
    return random.choice(UA)

"""determine the coordinate range of target area"""
def get_subregion_download_range(area):
    html = requests.get(f'https://nominatim.openstreetmap.org/search?format=json&q={area}')
    if html.text=='[]':
        print('Unable to query the address,please try other keys')
        sys.exit(0)
    else:
        info = eval(html.text)[0]
        return info['boundingbox']

"""download .osm file for OverpassDownloader"""
def download_osmfile_from_url(url, osm_filename):
    user_agent = fake_requests_headers()
    # Streaming, so we can iterate over the response
    resp = requests.get(url, stream=True, headers={"User-Agent": user_agent})
    if resp.status_code == 429:
        print("\033[31m Error! Too many requests, please try again later, or try to use random header.[0m", end=" ")
        return
    if resp.status_code==400:
        print(resp.text)
        return
    total_size = resp.content.__sizeof__()-33 # Total size in bytes
    block_size = 1024*1024
    wrote = 0

    with open(osm_filename, mode='wb') as f:
        for data in resp.iter_content(block_size, decode_unicode=True):
            wrote = wrote + len(data)
            print("\033[31m \r download progress：%.2f MB(%.2f MB)\033[0m" % (wrote /block_size,total_size/block_size), end=" ")
            try:
                f.write(data)
            except TypeError:
                f.write(data.encode())
            time.sleep(0.2)
        f.close()
    resp.close()
    print()
    if total_size != 0 and wrote != total_size:
        print("ERROR, something went wrong!")

