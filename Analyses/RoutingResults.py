import pickle
import geopandas
import pandas as pd
import osmnx as ox
import networkx as nx
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from shapely.geometry import Point
import sys
sys.path.append('..')

from NETX_Functions.GraphOperations import get_SP_distance, projectPointOnEdge
from NETX_Functions.PrintStuff import addGraph, addEdge
from NETX_Functions.MathOperations import computeLengthLinestring

exec(open("./SETTINGS_ANALYSES.py").read())

# Load graphs
with open(PATH_TO_INITIAL_GRAPH, "rb") as input_file: G_original = pickle.load(input_file)
with open(PATH_TO_EXTENDED_GRAPH, "rb") as input_file: G_extended = pickle.load(input_file)
used_crs = G_original.graph["crs"] # G_extended.graph["crs"] is the same

# Restrict the graphs to only the driveable roads
used_road_types = ['trunk','primary','secondary','tertiary', 'unclassified', 'residential', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'] # Roads + Road links

def elementList(list_with_elements, list_to_check):
    if type(list_with_elements) is list:
        for element in list_with_elements:
            if element in list_to_check: return True
    else: 
        if list_with_elements in list_to_check: return True
    return False

EL = [(u,v,k) for u,v,k,d in G_original.edges(keys = True, data=True) if elementList(d['highway'], used_road_types)]
G_original = G_original.edge_subgraph(EL)
EL = [(u,v,k) for u,v,k,d in G_extended.edges(keys = True, data=True) if (elementList(d['highway'], used_road_types) | d['driven'])]
G_extended = G_extended.edge_subgraph(EL)

# Project the graphs
G_original_projected = ox.project_graph(G_original, to_crs='epsg:4326') 
G_extended_projected = ox.project_graph(G_extended, to_crs='epsg:4326') 
# nodes, edges = ox.graph_to_gdfs(G_extended)
# print(nodes)
# print(edges)

# Load from/to combinations
fromto_points = pd.read_csv(PATH_TO_FROMTO_COMBINATIONS, sep = ";", index_col = 0, low_memory = False)

# Project point on edge (check if close enough for projection)
from_points = geopandas.GeoDataFrame(fromto_points, geometry = geopandas.points_from_xy(fromto_points.Longitude_from, fromto_points.Latitude_from), crs="EPSG:4326")
from_points = ox.project_gdf(from_points, to_crs = used_crs)
from_points = from_points.geometry
to_points = geopandas.GeoDataFrame(fromto_points, geometry = geopandas.points_from_xy(fromto_points.Longitude_to, fromto_points.Latitude_to), crs="EPSG:4326")
to_points = ox.project_gdf(to_points, to_crs = used_crs)
to_points = to_points.geometry

EDGES_ORIGINAL = G_original.edges(data='geometry', keys = True)
EDGES_EXTENDED = G_extended.edges(data='geometry', keys = True)

# Determine a list with unique OD pairs
if FIND_UNIQUE_ODS: 
    unique_SPs = [0]
    ind = 0
    for from_point, to_point in zip(from_points, to_points):
        # Print progress
        try: 
            if ind%(int(len(from_points)/100))==0: print("Working on point: " + str(ind) + ", " + str(ind/(int(len(from_points)/100)))+"%", end="\r")
        except: print("Working on point: " + str(ind))
        
        """----------------------------------------------------------------------------------"""
        add = True
        """----------------------------------------------------------------------------------"""
        for sp_ind in unique_SPs:
            dist_from = from_points[sp_ind].distance(from_point)
            dist_to = to_points[sp_ind].distance(to_point)
            if (dist_from <= CLOSENESSRADIUS) & (dist_to <= CLOSENESSRADIUS):
                add = False
                break
        if add:
            unique_SPs += [ind]
        ind+=1
    # Save unique OD pairs
    with open("UniqueSPs_"+str(CLOSENESSRADIUS)+".txt", "w") as output: output.write(str(unique_SPs))

def get_2_nearest_edges(edgs, point, return_dist=False):
    edge_distances = [(edge, point.distance(edge[3])) for edge in edgs]
    edge_distances_sorted = sorted(edge_distances, key = lambda x: x[1])
    return edge_distances_sorted[0:10] # For computation reasons

def plot_path(G, origin_point, destination_point, paths):
    # Create figure
    fig = go.Figure()

    # Draw basemap (OSM)
    fig.update_layout(mapbox1 = dict(center = dict(lon= fromto_points.Longitude_from[0],lat =fromto_points.Latitude_from[0]), accesstoken = mapbox_accesstoken, zoom = 13), margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="light")
    
    # Only print the relevant part of the network
    nodes_used_extended = [[t[0]] + [t[1]] for t in paths]
    nodes_used_extended = [item for sublist in nodes_used_extended for item in sublist]
    
    # Print the graph
    fig = addGraph(fig, G.subgraph(nodes_used_extended), ['red', 'red'], include_existing = True)
    
    # Add all the individual edge parts of the shortest path
    for e in paths:
        e = (e[0], e[1], e[2], ox.projection.project_geometry(e[3], crs=used_crs, to_crs='epsg:4326')[0])
        fig = addEdge(fig, e)
    
    # Print the origin and destination point
    origin_point = ox.projection.project_geometry(Point(origin_point), crs = used_crs,to_latlong=True)[0]
    fig.add_trace(go.Scattermapbox(mode='markers', lat=[origin_point.y], lon=[origin_point.x], visible = True, text = "Origin", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    destination_point = ox.projection.project_geometry(Point(destination_point), crs = used_crs,to_latlong=True)[0]
    fig.add_trace(go.Scattermapbox(mode='markers', lat=[destination_point.y], lon=[destination_point.x], visible = True, text = "Destination", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    
    ################################################################ ADD PROJ_POINT OF AN EDGE (RED) ###############################################################
    #proj_point = ox.projection.project_geometry(Point(205734.13828451364, -39024.15897507633), crs = used_crs,to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[proj_point.y], lon=[proj_point.x], visible = True, text = "Projection", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    ################################################################################################################################################################
    #proj_point = ox.projection.project_geometry(Point(204646.862610691, -39775.039426025236), crs = used_crs,to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[proj_point.y], lon=[proj_point.x], visible = True, text = "Projection", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    ################################################################################################################################################################
    
    # Add the nodes, because it looks nicer
    fig = addGraph(fig, G.subgraph(nodes_used_extended), ['red', 'red'], include_existing = True, only_nodes = True)
        
    # Launch app
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id = 'fig2', children=[dcc.Graph(id='fig',figure=fig, style={"height" : "95vh"})], style={"height" : "80vh"})], className = "container" )
    if __name__ == '__main__':
        app.run_server(debug=False)
    ################################################################################################################################################################

# Loop through all from and to points
df = pd.DataFrame(columns = ['From', 'To', "SP_OLD", "SP_NEW", "Diff", "From_projected", 'Minimal_projection_distance_from','From_projected_distance', "To_projected", 'Minimal_projection_distance_to', 'To_projected_distance', "From_projected_NEW", 'Minimal_projection_distance_from_NEW', 'From_projected_distance_NEW', "To_projected_NEW", 'Minimal_projection_distance_to_NEW', 'To_projected_distance_NEW', 'Distance_between_from', 'Distance_between_to'])
if (SELECTION is not None):
    from_points = from_points[SELECTION]
    to_points = to_points[SELECTION]
idn = 0

for from_point, to_point in zip(from_points, to_points):
    # Print progress
    try: 
        if idn%(int(len(from_points)/100))==0: print("Working on point: " + str(idn) + ", " + str(idn/(int(len(from_points)/100)))+"%", end="\r")
    except: print("Working on point: " + str(idn))
    
    """----------------------------------------------------------------------------------"""
    """----------------------------------------------------------------------------------"""
    # Define the possible from_points 
    possible_from_points = []
    closestEdges_FROM = get_2_nearest_edges(EDGES_ORIGINAL, from_point, return_dist = True)
    minimal_projection_distance_from_OLD = closestEdges_FROM[0][1]
    if closestEdges_FROM[0][1] < MAX_PROJECTION:
        possible_from_points += [((from_point.x, from_point.y), closestEdges_FROM[0][0])]    
    i = 1
    while ((closestEdges_FROM[i][1] - closestEdges_FROM[0][1]) < MAX_DISTANCE_OPPOSITE_EDGE) & (closestEdges_FROM[i][1] < MAX_PROJECTION):
        possible_from_points += [((from_point.x, from_point.y), closestEdges_FROM[i][0])]
        if i == len(closestEdges_FROM)-1: break
        else: i += 1

    # Define the possible to_points 
    possible_to_points = []
    closestEdges_TO = get_2_nearest_edges(EDGES_ORIGINAL, to_point, return_dist = True)
    minimal_projection_distance_to_OLD = closestEdges_TO[0][1]
    if closestEdges_TO[0][1] < MAX_PROJECTION:
        possible_to_points += [((to_point.x, to_point.y), closestEdges_TO[0][0])]   
    i = 1
    while ((closestEdges_TO[i][1] - closestEdges_TO[0][1]) < MAX_DISTANCE_OPPOSITE_EDGE) & (closestEdges_TO[i][1] < MAX_PROJECTION):
        possible_to_points += [((to_point.x, to_point.y), closestEdges_TO[i][0])] 
        if i == len(closestEdges_TO)-1: break
        else: i += 1 
    
    SP_length_OLD, SP_edges_OLD = float('inf'), []
    from_point_projected, to_point_projected, pp_from, pp_to = None, None, float('inf'), float('inf')
    ind_from = 0
    for fp in possible_from_points:
        ind_to = 0
        for tp in possible_to_points:
            a, b, from_point_projected_temp, to_point_projected_temp = get_SP_distance(G_original, fp, tp)
            if a < SP_length_OLD:
                pp_from = closestEdges_FROM[ind_from][1]
                pp_to = closestEdges_TO[ind_to][1]
                SP_length_OLD, SP_edges_OLD = a, b
                from_point_projected, to_point_projected = from_point_projected_temp, to_point_projected_temp        
            ind_to += 1
        ind_from += 1
           
    print("Original graph: " + str(SP_length_OLD)) 
    if PLOTPATH: plot_path(G_original_projected, from_point, to_point, SP_edges_OLD)
    """----------------------------------------------------------------------------------"""
    """----------------------------------------------------------------------------------"""
            
    """----------------------------------------------------------------------------------"""
    """----------------------------------------------------------------------------------"""
    # Define the possible from_points 
    possible_from_points = []
    closestEdges_FROM = get_2_nearest_edges(EDGES_EXTENDED, from_point, return_dist = True)
    minimal_projection_distance_from = closestEdges_FROM[0][1]
    if closestEdges_FROM[0][1] < MAX_PROJECTION:
        possible_from_points += [((from_point.x, from_point.y), closestEdges_FROM[0][0])]    
    i = 1
    while ((closestEdges_FROM[i][1] - closestEdges_FROM[0][1]) < MAX_DISTANCE_OPPOSITE_EDGE) & (closestEdges_FROM[i][1] < MAX_PROJECTION):
        possible_from_points += [((from_point.x, from_point.y), closestEdges_FROM[i][0])]
        if i == len(closestEdges_FROM)-1: break
        else: i += 1
    
    # Define the possible to_points 
    possible_to_points = []
    closestEdges_TO = get_2_nearest_edges(EDGES_EXTENDED, to_point, return_dist = True)
    minimal_projection_distance_to = closestEdges_TO[0][1]
    if closestEdges_TO[0][1] < MAX_PROJECTION:
        possible_to_points += [((to_point.x, to_point.y), closestEdges_TO[0][0])]    
    i = 1
    while ((closestEdges_TO[i][1] - closestEdges_TO[0][1]) < MAX_DISTANCE_OPPOSITE_EDGE) & (closestEdges_TO[i][1] < MAX_PROJECTION):
        possible_to_points += [((to_point.x, to_point.y), closestEdges_TO[i][0])]
        if i == len(closestEdges_TO)-1: break
        else: i += 1  
    
    SP_length_NEW, SP_edges_NEW = float('inf'), []
    from_point_projected_NEW, to_point_projected_NEW, pp_from_NEW, pp_to_NEW = None, None, float('inf'), float('inf')
    ind_from = 0
    for fp in possible_from_points:
        ind_to = 0
        for tp in possible_to_points:
            a, b, from_point_projected_temp, to_point_projected_temp = get_SP_distance(G_extended, fp, tp)
            if a < SP_length_NEW:
                pp_from_NEW = closestEdges_FROM[ind_from][1]
                pp_to_NEW = closestEdges_TO[ind_to][1]
                SP_length_NEW, SP_edges_NEW = a, b
                from_point_projected_NEW, to_point_projected_NEW = from_point_projected_temp, to_point_projected_temp
        ind_to += 1
    ind_from += 1
    
    print("Extended graph: " + str(SP_length_NEW))
    if PLOTPATH: plot_path(G_extended_projected, from_point, to_point, SP_edges_NEW)
    """----------------------------------------------------------------------------------"""
    """----------------------------------------------------------------------------------"""   
       
    """----------------------------------------------------------------------------------"""
    """----------------------------------------------------------------------------------"""
    try: distance_between_from = Point(from_point_projected).distance(Point(from_point_projected_NEW))
    except: #print("At least one of the from points could not be projected!")
        distance_between_from = float('inf')
    try: distance_between_to = Point(to_point_projected).distance(Point(to_point_projected_NEW))
    except: #print("At least one of the to points could not be projected!")
        distance_between_to = float('inf')

    # Save and move to next iteration....
    df.loc[len(df)] = [from_point, to_point, SP_length_OLD, SP_length_NEW, SP_length_OLD - SP_length_NEW, from_point_projected, minimal_projection_distance_from_OLD, pp_from, to_point_projected,minimal_projection_distance_to_OLD, pp_to, from_point_projected_NEW, minimal_projection_distance_from, pp_from_NEW, to_point_projected_NEW,minimal_projection_distance_to, pp_to_NEW,distance_between_from, distance_between_to]
    
    idn += 1
    if idn % 100 == 0:
       df.to_csv(FNAME, sep = ";")
       
df.to_csv(FNAME, sep = ";")
    
