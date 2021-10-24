# OSM2Rail: An open-source education tool for constructing modeling datasets of railway transportation
**Authors**: Jiawei Lu, Qian Fu, Zanyang Cui, Dr. Junhua Chen

**Email**: jiaweil9@asu.edu, q.fu@bham.ac.uk, zanyangcui@outlook.com, cjh@bjtu.edu.cn
## Introduction
The python tool of OSM2Rail is an integrated and enhanced version of two python packages, namely [OSM2GMNS](https://pypi.org/project/osm2gmns/) and [Pydriosm](https://pypi.org/project/pydriosm/). The former aims to convert [OpenStreetMap](https://www.openstreetmap.org/) data to generic node and link files in GMNS format, while the latter aims to enable a batch process of downloading, reading and PostgreSQL-based I/O of OpenStreetMap data.

OSM2GMNS is currently developed and maintained by Jiawei Lu and Dr. Xuesong Zhou at Arizona State University. PyDriosm published by Dr. Qian Fu at Birmingham Centre for Railway Research and Education, University of Birmingham, is an open-source tool for researchers or practitioners to easily download and read OSM map data in popular file formats such as protocolbuffer binary format (PBF) and shapefile, which are available for free download from Geofabrik and BBBike. This package also provides a convenient way for PostgreSQL-based I/O and storage of parsed OSM data.

Integrating the data conversion and online data downloading capabilities from the above 2 packages, OSM2Rail allows users to rapidly obtain OSM data for a given set of areas and convert them to node, link, and poi files for further system modeling and optimization. Users are recommended to download OSM map data in .osm or .osm.pbf format and convert them to commonly used csv files.

## Requirements
- bs4
- matplotlib<=3.3.0
- osmium
- fuzzywuzzy

## Installation
```python
pip install osm2rail
```
>Note
> - For Windows users, the _pip_ method might fail to install some dependencies. If errors occur when you try to install any of those dependencies, try instead to pip install their .whl files, which can be downloaded from the Unoffical Windows Binaries for [Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/).

## Simple Example
```python
import osm2rail as orl

"""Step 1: download OSM data in .osm format from Overpass"""
subarea="IHB Blue Island Yard"
download_dir='osmfile'
osm_file=orl.download_osm_data_from_overpass(subarea_names=subarea,download_dir=download_dir,ret_download_path=True)

"""Step 2: convert OSM data in .osm format to GMNS-rail network files"""
net=orl.get_network_from_file(osm_filename=osm_file[0],strict_mode=True,POIs=True)

"""Step 3: visualize rail network data set"""
orl.showNetwork(net)

"""Step 4: output Networks to CSV"""
orl.saveNetwork(net)
```
<img src="https://github.com/PariseC/osm2rail/blob/main/media/IHB%20Blue%20Island%20Yard.png?raw=true" width="800" height="600" alt="all modes network"/><br/>

## User guide
Users can check the [user guide](https://github.com/PariseC/osm2rail/tree/main/doc) for a detailed introduction of osm2rail.
