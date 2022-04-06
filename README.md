# OSM2Rail
**An open-source education tool for constructing modeling datasets of railway transportation**

Authors: Jiawei Lu, Qian Fu, Zanyang Cui, Dr. Junhua Chen

Email: jiaweil9@asu.edu, q.fu@bham.ac.uk, zanyangcui@outlook.com, cjh@bjtu.edu.cn

---

# Introduction
The python tool of OSM2Rail is an integrated and enhanced version of two python packages, namely [OSM2GMNS](https://pypi.org/project/osm2gmns/) and [Pydriosm](https://pypi.org/project/pydriosm/). The former aims to convert [OpenStreetMap](https://www.openstreetmap.org/) data to generic node and link files in GMNS format, and the latter aims to enable a batch process of downloading, reading and PostgreSQL-based I/O of OpenStreetMap data.

OSM2GMNS is currently developed and maintained by Jiawei Lu and Dr. Xuesong Zhou at Arizona State University. PyDriosm published by Dr. Qian Fu at Birmingham Centre for Railway Research and Education, University of Birmingham, is an open-source tool for researchers or practitioners to easily download and read OSM map data in popular file formats such as protocolbuffer binary format (PBF) and shapefile, which are available for free download from Geofabrik and BBBike. This package also provides a convenient way for PostgreSQL-based I/O and storage of parsed OSM data.

Integrating the data conversion and online data downloading capabilities from the above 2 packages, OSM2Rail allows users to rapidly obtain OSM data for a given set of areas and convert them to node, link, and poi files for further system modeling and optimization. Users are recommended to download OSM map data in .osm or .osm.pbf format and convert them to commonly used csv files.

# Requirements
- bs4
- osmium
- shapely
- matplotlib
- fuzzywuzzy
- shapely
- pandas
- numpy
- requests

## Features

- [x] Download and parse OpenStreetMap (OSM) data in popular file formats such as protocolbuffer binary format (.osm.pbf) and XML format (.osm)
- [x] Export railway elements from OSM data to node, link and poi files
- [x] Support exporting railway elements with specified names
- [x] Export railway elements as csv file in GMNS format
- [x] Support QGIS to open output files

# Installation
```python
pip install osm2rail
```

> Note
> For Windows users, the pip method might fail to install some dependencies. If errors occur when you try to install any of those dependencies, try instead to pip install their .whl files, which can be downloaded from the Unoffical Windows Binaries for [Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/).

# Quick start
**Step1: download OSM data from OSM**
```python
import osm2rail as orl
subarea_name = 'IHB Blue Island Yard'
download_dir = './osmfile'
osm_file=orl.download_osm_data_from_overpass(subarea_names=subarea_name,download_dir = download_dir,ret_download_path=True)
```
**output:**
>The box of IHB_Blue_Island_Yard is ['41.6372039', '41.642362', '-87.6599743', '-87.6294597'] 
  download progress：0.64 MB(0.64 MB) 
Done.

**Step2: convert OSM data in .osm format to GMNS-rail network files**
```python
net=orl.get_network_from_file(filename=osm_file[0],POIs=True,check_boundary=True)
```

**Step3: visualize rail network**
```python
orl.show_network(net)
```
**output:**
![IHB Blue Island Yard](https://github.com/PariseC/osm2rail/blob/main/media/IHB%20Blue%20Island%20Yard.png?raw=true)

**Step4: save rail network to CSV file**
```python
orl.save_network(net,output_folder='./csvfile')
```

# Advance Usage
**Step1: prepare an osm map file**
*Here we manually downloaded the map file of the city of London through BBBike.*

![London City Network](https://github.com/PariseC/osm2rail/blob/main/media/London%20Rail%20Network-1.png?raw=true)

**Step2: specify the railway element name and parse the railnetwork.**
```python
# net=orl.get_network_from_file(filename='./osmfile/London.osm',POIs=True)
# specify the railway element
net=orl.get_network_from_file(filename='./osmfile/London.osm',POIs=True,target_elements=['South London Line']) 
```

**Step3: visualize rail network**
```python
orl.show_network(net)
```
**output:**
All rail lines:
![all lines](https://github.com/PariseC/osm2rail/blob/main/media/London%20Rail%20Network-2.png?raw=true)

South London Line:
![South London Line](https://github.com/PariseC/osm2rail/blob/main/media/South%20London%20Line.png?raw=true)
**Step4: save rail network to CSV file**
```python
orl.save_network(net,output_folder='./csvfile')
```


# Sample Networks

## Beijing-Tianjin Intercity Railway
![Beijing-Tianjin Intercity Railway](https://github.com/PariseC/osm2rail/blob/main/media/Beijing-Tianjin%20Intercity%20Railway.png?raw=true)

## Beijing South Railway Station
![Beijing South Railway Station](https://github.com/PariseC/osm2rail/blob/main/media/1.png?raw=true)

## Shanghai Hongqiao Railway Station
![Shanghai Hongqiao Railway Station](https://github.com/PariseC/osm2rail/blob/main/media/2.png?raw=true)

## Frankfurt
![Frankfurt](https://github.com/PariseC/osm2rail/blob/main/media/7.png?raw=true)

## BNSF Argentine Yard
![BNSF Argentine Yard](https://github.com/PariseC/osm2rail/blob/main/media/BNSF%20Argentine%20Yard.png?raw=true)

---

## 
# Update log

## 2022.04.06-v0.0.6

- **Added**: Add the 'target_elements' field to parse the rail network with the given names.
- **Changed**: Change 'strict_mode' to 'check_boundary'.
- **Changed**: Adjust railway key fields.

# License

Apache Software License (Apache License 2.0).


