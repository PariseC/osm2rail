import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection,PolyCollection

def show_network(network,filename=None,dpi=150):
    """
    :param network: network class
    :param filename: str
    :param dpi: int
    :return:
    """
    node_x_coords=[]
    node_y_coords=[]
    link_coords=[]
    poi_coords=[]

    for _,node in network.node_dict.items():
        node_x_coords.append(node.x_coord)
        node_y_coords.append(node.y_coord)

    for _,link in network.link_dict.items():
        coords = list(link.geometry.coords)
        link_coords.append(np.array(coords))

    if len(network.POI_list):
        for poi in network.POI_list:
            coords = list(poi.geometry.exterior.coords)
            poi_coords.append(np.array(coords))

    fig, ax = plt.subplots(figsize=(12, 8))
    # plot network nodes
    ax.scatter(node_x_coords, node_y_coords, marker='o', c='red', s=10, zorder=1)
    # plot network links
    ax.add_collection(LineCollection(link_coords, colors='orange', linewidths=1, zorder=2))
    # plot network pois
    if len(poi_coords):
        coll = PolyCollection(poi_coords, alpha=0.7, zorder=0)
        ax.add_collection(coll)
    # set axis
    ax.autoscale_view()
    plt.xlabel('x_coord')
    plt.ylabel('y_coord')
    plt.tight_layout()
    # show fig
    plt.show()
    # save fig
    if filename:
        try:
            figname = filename+'network.png'
            fig.savefig(figname, dpi=dpi, bbox_inches='tight')
        except Exception as e:
            print(e)