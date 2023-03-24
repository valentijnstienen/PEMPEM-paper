import pickle
import osmnx as ox
import os
import numpy as np
import pandas as pd
import geopandas
from shapely import wkt
from math import sqrt
import ast 

import simp_functions_GB.simplification as ss


def elementList(list_with_elements, list_to_check):
    if type(list_with_elements) is list:
        for element in list_with_elements:
            if element in list_to_check: return True
    elif list_with_elements[0] == "[":
        l = ast.literal_eval(list_with_elements)
        for element in l:
            if element in list_to_check: return True
    else: 
        if list_with_elements in list_to_check: return True
    return False
def create_shapefile(gdf, filename):

    try: gdf['osmid'] = [str(l) for l in gdf['osmid']]
    except: a = 1

    try:
        a = gdf.x
        attributes = ['x','y', 'lon', 'lat', 'ref', 'highway']
        for attr in attributes:
            try: gdf[attr] = [str(l) for l in gdf[attr]]
            except: a = 1
    except:
        attributes = ['Start_pos', 'End_pos', 'osm_type', 'highway', 'oneway', 'surface', 'access', 'junction', 'name', 'old_name', 'bridge', 'layer', 'accuracy', 'name:etymo', 'email', 'descriptio', 'loc_name', 'PFM:RoadID', 'PFM:garmin', 'smoothness', 'est_width', 'lanes', 'maxspeed','lanes:back', 'lanes:forw', 'tracktype', 'bicycle', 'foot', 'horse', 'sac_scale', 'trail_visi', 'mtb:scale', 'ford', 'maxheight','motor_vehi', 'width', 'barrier', 'service', 'waterway', 'check_date', 'import', 'cutting', 'segregated', 'wheelchair', 'abandoned:','abandone_1', 'cycleway', 'sidewalk', 'embankment', 'lit', 'tunnel','Observatio', 'seasonal', 'wikidata', 'ref', 'start_date', 'alt_name','name:en', 'mtb:scale:', 'covered', 'intermitte', 'noname', 'crossing','footway', 'bridge:str', 'official_n', 'man_made', 'incline','informal']
        for attr in attributes:
            try: gdf[attr] = [str(l) for l in gdf[attr]]
            except: a = 1

        try: gdf = gdf.drop(['close_to_point_start', 'close_to_point_end'], axis=1)
        except: a = 1

    gdf.to_file(filename)
def computeLengthLinestring(line, method = "haversine"):
    """
     Returns the length of the linestring [line], using the [method].
    
     Parameters
     ----------
     line : LineString
     method : string 
        determines how to compute the length between points (e.g, haversine or euclidean)

     Returns
     -------
     distance : float
         length of the [line]
    
    """
    # Extract all coordinates
    numCoords = len(line.coords) - 1
    
    distance = 0
    for i in range(0, numCoords):
        point1 = line.coords[i]
        point2 = line.coords[i + 1]
        if method == "haversine": distance += haversine(point1[0], point1[1], point2[0], point2[1])
        else: distance += sqrt((point1[0]-point2[0])**2 + (point1[1] - point2[1])**2)
    return distance
def print_edge_info_WB(edges):
    relevant_edges = edges
    total_km = round(sum(edges['length'])/1000,0)
    total_km_added = total_km - 6009 #OE: 6858, EO: 6009
    print("--------------------------------------------")
    print("Total amount of km:", total_km) #WB /2
    print("# of edges:", len(relevant_edges))
    print("Total amount of km added:",total_km_added)
    print("--------------------------------------------")
def print_edge_info_PEMPEM(edges):
    edges.highway = edges.highway.astype(str)
    
    # Pre-process the graph, restrict the graphs to only the driveable roads and project it
    used_road_types = ['trunk','primary','secondary','tertiary', 'unclassified', 'residential', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'] # Roads + Road links
    relevant_edge_indices = [i for i in edges.index if (elementList(edges.loc[i,'highway'], used_road_types) | edges.loc[i,'driven'])]
    relevant_edges = edges.iloc[relevant_edge_indices].reset_index(drop=True)
    
    #relevant_edges = edges[edges['highway'].apply(lambda s: s in driveable_types) | edges['driven']].reset_index(drop=True)
    total_km = round(sum(relevant_edges['length'])/1000,0)
    total_km_added = total_km - 6859 #PEMPEM: 6712
    geom_not_osm = round(sum(relevant_edges[relevant_edges.new]['length'])/1000,0)
    print("--------------------------------------------")
    print("Total amount of km:", total_km) #WB /2
    print("# of edges:", len(relevant_edges))
    print("Total amount of km added:",total_km_added)
    print("      Geometry in OSM:", (total_km_added - geom_not_osm))
    print("      Geometry not in OSM:",geom_not_osm,"km")
    print("--------------------------------------------")
def csvs2graph(path_nodes, path_edges, project = True):
    edges = pd.read_csv(path_edges, sep=";", index_col = 0, low_memory = False) #PEMPEM: 14960, OE: 1100, EO: 8000
    nodes = pd.read_csv(path_nodes, sep=";", index_col = 0, low_memory = False) #PEMPEM: 14960, OE: 1100, EO: 8000
    nodes['geometry'] = nodes['geometry'].apply(wkt.loads)
    edges['geometry'] = edges['geometry'].apply(wkt.loads)
    
    try: edges.loc[edges['highway'].isnull(), 'highway'] = "-"
    except: print("No highway in the dataset...")
    
    gdf_nodes = geopandas.GeoDataFrame(nodes, geometry=nodes.geometry, crs='epsg:4326')
    gdf_edges = geopandas.GeoDataFrame(edges, geometry=edges.geometry, crs='epsg:4326')
    
    # Selection of attributes
    #gdf_nodes = gdf_nodes[['x','y', 'geometry']]
    #gdf_edges = gdf_edges[['geometry', 'u', 'v', 'key', 'length']]
    G = ox.graph_from_gdfs(gdf_nodes, gdf_edges, graph_attrs = {'crs': 'epsg:4326', 'simplified': True})
    if project: G = ox.projection.project_graph(G)# to_crs="+proj=utm +zone=48 +ellps=WGS84 +datum=WGS84 +units=m +no_defs +type=crs"
    return G

def simplify_graph_WB(path_nodes_or_pickle, path_edges = None):
    """ ------------------  Load graph  ------------------ """
    if path_nodes_or_pickle[-6:] == "pickle": # using a specified pickle file
        with open(path_nodes_or_pickle, "rb") as input_file: G = pickle.load(input_file)
        nodes, edges = ox.graph_to_gdfs(G)
    else: # using specified .csv files (folder)
        G = csvs2graph(path_nodes = path_nodes_or_pickle, path_edges = path_edges)
        nodes, edges = ox.graph_to_gdfs(G)
    """ ------------------------------------------------- """
    
    # Create nodes/edges
    print("Info before simplifying")
    print_edge_info_WB(edges)
    
    # interstitual points that should be removed according to OSMnx
    # nc = ['r' if ss._is_endpoint(G, node) else 'y' for node in G.nodes()]
    # ox.plot_graph(G, node_color=nc)
    
    """-------------------------------------------------"""
    """------ Remove the 0-length self loops -----------"""
    """-------------------------------------------------"""
    edges = list(G.edges(data=True, keys = True))
    for edge in edges:
        G= ss._is_self_loop(G, edge, bool_ = False)
    """-------------------------------------------------"""
    
    """-------------------------------------------------"""
    """---- Remove the 1 -> node -> 1 (undirected) -----"""
    """-------------------------------------------------"""
    nodes = list(G.nodes())  
    nodes = [n for n in nodes if (not ss._is_endpoint(G, n, strict=True))]
    for node in nodes:
        G = ss._remove_nodes_undirected(G, node)
    """-------------------------------------------------""" 

    # interstitual points that remain according to OSMnx
    #nc = ['r' if ss._is_endpoint(G, node) else 'y' for node in G.nodes()]
    #ox.plot_graph(G, node_color=nc)
    
    # Save all information in different formats
    new_path = path_nodes_or_pickle.split("/")[0]+"/"+path_nodes_or_pickle.split("/")[1]
    # - Save simplified graph
    #with open(new_path+"/"+path.split("/")[2]+"graph_SIMPLE.pickle", "wb") as file: pickle.dump(G, file)
    # - Save nodes/edges
    nodes, edges = ox.graph_to_gdfs(G)
    print("Info after simplifying")
    print_edge_info_WB(edges)
    if not os.path.exists(new_path+"/_Graphs_SIMPLE"): os.makedirs(new_path+"/_Graphs_SIMPLE")
    nodes.to_csv(new_path+"/_Graphs_SIMPLE/Nodes.csv", sep = ";")
    edges.to_csv(new_path+"/_Graphs_SIMPLE/Edges.csv", sep = ";")
    # - Save new shapefiles
    if not os.path.exists(new_path+"/_Shapefiles_SIMPLE"): os.makedirs(new_path+"/_Shapefiles_SIMPLE")
    create_shapefile(nodes, new_path+"/_Shapefiles_SIMPLE/NODES.shp")
    create_shapefile(edges, new_path+"/_Shapefiles_SIMPLE/EDGES.shp")
    print("============================================")

def simplify_graph_PEMPEM(path_nodes_or_pickle, path_edges = None):
    """ ------------------  Load graph  ------------------ """
    if path_nodes_or_pickle[-6:] == "pickle": # using a specified pickle file
        with open(path_nodes_or_pickle, "rb") as input_file: G = pickle.load(input_file)
        nodes, edges = ox.graph_to_gdfs(G)
    else: # using specified .csv files (folder)
        G = csvs2graph(path_nodes = path_nodes_or_pickle, path_edges = path_edges)
        nodes, edges = ox.graph_to_gdfs(G)
    """ ------------------------------------------------- """

    # Create nodes/edges
    print("Info before simplifying")
    print_edge_info_PEMPEM(edges)
    #
    # print(np.sum(edges.loc[edges.highway == 'unclassified', 'length']))
        
    """-------------------------------------------------"""
    """------ Remove the 0-length self loops -----------"""
    """-------------------------------------------------"""
    edges = list(G.edges(data=True, keys = True))
    for edge in edges:
        G= ss._is_self_loop(G, edge, bool_ = False)
    """-------------------------------------------------"""

    
    """-------------------------------------------------"""
    """--------- Remove the 1 -> node -> 1 -------------"""
    """-------------------------------------------------"""
    print("Removing the 1 -> node -> 1 nodes...")
    # See which nodes will be removed here
    #nc_old = ['y' if ss._is_easy_interstitual(G, node, bool_ = True) else 'r' for node in G.nodes()]
    #print("Remove", nc_old.count('y'), "(", np.round((nc_old.count('y')/len(nc_old))*100,1), "%) nodes.")
    # ox.plot_graph(G, node_color=nc_old)
    nodes = list(G.nodes())
    for node in nodes:#['Start node: 100_0/Node_p: 105_3']:
        G = ss._is_easy_interstitual(G, node, bool_ = False)
    #nc = ['y' if ss._is_easy_interstitual(G, node, bool_ = True) else 'r' for node in G.nodes()]
    #print(nc_old.count('y'), "(", np.round((nc_old.count('y')/len(nc_old))*100,1), "%) nodes removed.")
    #ox.plot_graph(G, node_color=nc)
    """-------------------------------------------------"""
    
    # _, edges = ox.graph_to_gdfs(G)
    # print(np.sum(edges.loc[edges.highway == 'unclassified', 'length']))
    
    """-------------------------------------------------"""
    """------ Remove the 2 -> node -> 2 ----------------"""
    """-------------------------------------------------"""
    print("Removing the 2 -> node -> 2 nodes...")
    # See which nodes will be removed here
    #nc_old = ['y' if ss._is_difficult_interstitual(G, node, bool_ = True) else 'r' for node in G.nodes()]
    #print("Remove", nc_old.count('y'), "(", np.round((nc_old.count('y')/len(nc_old))*100,1), "%) nodes.")
    #ox.plot_graph(G, node_color=nc_old)
    nodes = list(G.nodes())
    for node in nodes:#['Node_p: 1169_27']:#nodes:#['End node: 4240_47/Node_p: 4241_1/End node: 4241_4/Node_p: 4242_2']:
        G, c = ss._is_difficult_interstitual(G, node, bool_ = False)
        # if c == 1:
        #     print(node)
        #     nodes, edges = ox.graph_to_gdfs(G)
        #     print_edge_info(edges)
    #nc = ['y' if ss._is_difficult_interstitual(G, node, bool_ = True) else 'r' for node in G.nodes()]
    #print(nc_old.count('y'), "(", np.round((nc_old.count('y')/len(nc_old))*100,1), "%) nodes removed.")
    #ox.plot_graph(G, node_color=nc)
    """-------------------------------------------------"""
    
    # _, edges = ox.graph_to_gdfs(G)
    # print(np.sum(edges.loc[edges.highway == 'unclassified', 'length']))
    
    # interstitual points that remain according to OSMnx
    #nc = ['r' if ss._is_endpoint(G, node) else 'y' for node in G.nodes()]
    #ox.plot_graph(G, node_color=nc)

    # Save all information in different formats
    new_path = path_nodes_or_pickle.split("/")[0]+"/"+path_nodes_or_pickle.split("/")[1]
    # - Save simplified graph
    #with open(new_path+"/"+path_nodes_or_pickle.split("/")[2]+"/"+"graph_SIMPLE.pickle", "wb") as file: pickle.dump(G, file)
    # - Save nodes/edges
    nodes, edges = ox.graph_to_gdfs(G)
    print("Info after simplifying")
    print_edge_info_PEMPEM(edges)
    # if not os.path.exists(new_path+"/_Graphs_SIMPLE"): os.makedirs(new_path+"/_Graphs_SIMPLE")
    # nodes.to_csv(new_path+"/_Graphs_SIMPLE/Nodes.csv", sep = ";")
    # edges.to_csv(new_path+"/_Graphs_SIMPLE/Edges.csv", sep = ";")
    # # - Save new shapefiles
    # if not os.path.exists(new_path+"/_Shapefiles_SIMPLE"): os.makedirs(new_path+"/_Shapefiles_SIMPLE")
    # create_shapefile(nodes, new_path+"/_Shapefiles_SIMPLE/NODES.shp")
    # create_shapefile(edges, new_path+"/_Shapefiles_SIMPLE/EDGES.shp")
    print("============================================")

################## WORLDBANK ##################
# print("Starting graph WB (OE)")
# simplify_graph_WB(path_nodes_or_pickle="graphs/OE/graph_0-0.pickle") #NOTE THESE ARE DIRECTED GRAPHS!!!
# print("Starting graph WB (EO)")
# simplify_graph_WB(path_nodes_or_pickle="graphs/EO/graph_0-0.pickle") #NOTE THESE ARE DIRECTED GRAPHS!!!
print("Extended graph WB (OE)")
simplify_graph_WB(path_nodes_or_pickle="graphs/OE/_Graphs/Nodes_0_1100.csv", path_edges = "graphs/OE/_Graphs/Edges_0_1100.csv")
print("Extended graph WB (EO)")
simplify_graph_WB(path_nodes_or_pickle="graphs/EO/_Graphs/Nodes_0_8000.csv", path_edges = "graphs/EO/_Graphs/Edges_0_8000.csv")
###############################################

#################### PEMPEM ###################
# print("Starting graph PEMPEM")
# simplify_graph_PEMPEM(path_nodes_or_pickle="graphs/PEMPEM_START/graph_0-0.pickle")
# for case in ['00', '0', '1', '2']:#, '0', '1', '2']:
#     print("Extended graph PEMPEM (Case:", case + ")")
#     simplify_graph_PEMPEM(path_nodes_or_pickle="graphs/PEMPEM_"+case+"/_Graphs/Nodes_0_14960.csv", path_edges="graphs/PEMPEM_"+case+"/_Graphs/Edges_0_14960.csv" )
###############################################
