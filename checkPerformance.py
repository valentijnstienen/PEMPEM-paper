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
import ast
import numpy as np
#sys.path.append('..')
import math

from NETX_Functions.GraphOperations import get_SP_distance, projectPointOnEdge
from NETX_Functions.PrintStuff import addGraph, addEdge, create_shapefile
from NETX_Functions.MathOperations import haversine, computeLengthLinestring

def elementList(list_with_elements, list_to_check):
    if type(list_with_elements) is list:
        for element in list_with_elements:
            if element in list_to_check: return True
    else: 
        if list_with_elements in list_to_check: return True
    return False
def get_2_nearest_edges(edgs, point, return_dist=False):
    edge_distances = [(edge, point.distance(edge[3])) for edge in edgs]
    edge_distances_sorted = sorted(edge_distances, key = lambda x: x[1])
    return edge_distances_sorted[0:10] # For computation reasons
def determine_possible_fromto_points(edges, point, MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE):
    # Define the possible from_points 
    possible_points = []
    closestEdges = get_2_nearest_edges(edges, point, return_dist = True)
    minimal_projection_distance_OLD = closestEdges[0][1]
    if closestEdges[0][1] < MAX_PROJECTION:
        possible_points += [((point.x, point.y), closestEdges[0][0])]    
    if len(closestEdges) == 1: return possible_points
    i = 1
    while ((closestEdges[i][1] - closestEdges[0][1]) < MAX_DISTANCE_OPPOSITE_EDGE) & (closestEdges[i][1] < MAX_PROJECTION):
        possible_points += [((point.x, point.y), closestEdges[i][0])]
        if i == len(closestEdges)-1: break
        else: i += 1
    return possible_points 
def determine_best_shortest_path(G, possible_from_points, possible_to_points):
    SP_length, SP_edges = float('inf'), []
    from_point_projected, to_point_projected = None, None
    ind_from = 0
    for fp in possible_from_points:
        ind_to = 0
        for tp in possible_to_points:
            a, b, from_point_projected_temp, to_point_projected_temp = get_SP_distance(G, fp, tp)
            if a < SP_length:
                SP_length, SP_edges = a, b
                from_point_projected, to_point_projected = from_point_projected_temp, to_point_projected_temp
            ind_to += 1
        ind_from += 1
    return SP_length, SP_edges, from_point_projected, to_point_projected
def plot_path(G, origin_point, destination_point, paths, fromto_points, mapbox_accesstoken):
    # Create figure
    fig = go.Figure()

    # Draw basemap (OSM)
    fig.update_layout(mapbox1 = dict(center = dict(lon= fromto_points.Longitude_from[0],lat =fromto_points.Latitude_from[0]), accesstoken = mapbox_accesstoken, zoom = 13), margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="light")

    used_crs = "+proj=utm +zone=48 +ellps=WGS84 +datum=WGS84 +units=m +no_defs +type=crs"
    
    # Only print the relevant part of the network
    nodes_used_extended = [[t[0]] + [t[1]] for t in paths]
    nodes_used_extended = [item for sublist in nodes_used_extended for item in sublist]

    # Print the graph
    fig = addGraph(fig, G.subgraph(nodes_used_extended), ['red', 'red'], include_existing = True)

    # Add all the individual edge parts of the shortest path
    for e in paths:
        e = (e[0], e[1], e[2], ox.projection.project_geometry(e[3], crs=used_crs, to_crs='epsg:4326')[0])#
        fig = addEdge(fig, e)

    # Print the origin and destination point
    origin_point = ox.projection.project_geometry(Point(origin_point),crs = used_crs, to_latlong=True)[0]#
    fig.add_trace(go.Scattermapbox(mode='markers', lat=[origin_point.y], lon=[origin_point.x], visible = True, text = "Origin", marker = {'size' : 15, 'opacity': 1, 'color': 'yellow', 'allowoverlap': True}))
    destination_point = ox.projection.project_geometry(Point(destination_point),crs = used_crs,to_latlong=True)[0]#crs = used_crs
    fig.add_trace(go.Scattermapbox(mode='markers', lat=[destination_point.y], lon=[destination_point.x], visible = True, text = "Destination", marker = {'size' : 15, 'opacity': 1, 'color': 'yellow', 'allowoverlap': True}))

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
    #if __name__ == '__main__':
    app.run_server(debug=False)
    ################################################################################################################################################################

def determine_greatness(G_original, G_extended, IDs, MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE, mapbox_accesstoken):
    # Pre-process the graph, restrict the graphs to only the driveable roads and project it
    used_road_types = ['trunk','primary','secondary','tertiary', 'unclassified', 'residential', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'] # Roads + Road links

    # ______________________ Load original OSM data ______________________#
    # # This is the extended graph but with nothing excluded (this is our comparison graph)
    EL = [(u,v,k) for u,v,k,d in G_original.edges(keys = True, data=True) if (d['driven'])]
    G_original = G_original.edge_subgraph(EL)
    G_original_projected = ox.project_graph(G_original, to_crs='epsg:4326')  # Project the graph
    EDGES_ORIGINAL = G_original.edges(data='geometry', keys = True) # All edges of the graph
    #_____________________________________________________________________#

    # _______________________ Load extended graph ________________________#
    EL = [(u,v,k) for u,v,k,d in G_extended.edges(keys = True, data=True) if (d['driven'])]
    G_extended = G_extended.edge_subgraph(EL)
    G_extended_projected = ox.project_graph(G_extended, to_crs='epsg:4326')  # Project the graph
    EDGES_EXTENDED = G_extended.edges(data='geometry', keys = True) # All edges of the graph 
    #_____________________________________________________________________#

    #______________________________ OD pairs _____________________________#
    PATH_TO_FROMTO_COMBINATIONS = "Data/PEMPEM/PEMPEM_stops_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv"
    relevant_ID_indices = list(np.array(IDs)-1)
    # Load from/to combinations
    fromto_points = pd.read_csv(PATH_TO_FROMTO_COMBINATIONS, sep = ";", index_col = 0, low_memory = False)
    # Project point on edge (check if close enough for projection)
    from_points = geopandas.GeoDataFrame(fromto_points, geometry = geopandas.points_from_xy(fromto_points.Longitude_from, fromto_points.Latitude_from), crs="EPSG:4326")
    from_points = ox.project_gdf(from_points)#, to_crs = used_crs)
    from_points = from_points.geometry
    from_points_relevant = from_points[relevant_ID_indices].reset_index(drop=True)
    to_points = geopandas.GeoDataFrame(fromto_points, geometry = geopandas.points_from_xy(fromto_points.Longitude_to, fromto_points.Latitude_to), crs="EPSG:4326")
    to_points = ox.project_gdf(to_points)#, to_crs = used_crs)
    to_points = to_points.geometry
    to_points_relevant = to_points[relevant_ID_indices].reset_index(drop=True)
    #_____________________________________________________________________#
    
    #_______________________ Lengths of trajectories _____________________#
    PATH_TO_TRAJECTORY_LENGTHS = "Data/PEMPEM/trajectories_lengths.csv"
    try: # lengths are already created
        trajectory_lengths = pd.read_csv(PATH_TO_TRAJECTORY_LENGTHS, sep = ";", index_col = 0, low_memory = False)
    except: # (ONLY NEEDED ONCE)
        PATH_TO_TRAJECTORIES = "Data/PEMPEM/PEMPEM_subtrips_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv"
        trajectories = pd.read_csv(PATH_TO_TRAJECTORIES, sep = ";", index_col = 0, low_memory = False)
        trajectories = trajectories.groupby('ID').agg({'Latitude':list, 'Longitude':list}).reset_index(drop = False)
        lengths = []
        for i in range(len(trajectories)):
            l = []
            for lat, lon in zip(trajectories.loc[i, 'Latitude'], trajectories.loc[i,'Longitude']):
                l+= [(lat, lon)]
            lengths += [computeLengthLinestring(LineString(l))]
        trajectories['Length'] = lengths
        trajectory_lengths = trajectories.loc[:, ['ID', 'Length']]
        # Save for later use
        trajectory_lengths.to_csv('Data/PEMPEM/trajectories_lengths.csv', sep = ";")
        #############################################################################################################
    trajectory_lengths_relevant = trajectory_lengths.Length[relevant_ID_indices].reset_index(drop=True)
    #_____________________________________________________________________#

    # Loop through all from and to points
    df = pd.DataFrame(columns = ['From', 'To', 'From_P_OLD', 'To_P_OLD', "SP_OLD", 'From_P_NEW', 'To_P_NEW', "SP_NEW"])
    idn = 0

    for from_point, to_point in zip(from_points_relevant, to_points_relevant):
        # Print progress
        try: 
            if idn%(int(len(from_points)/1000))==0: print("Working on point: " + str(idn) + ", " + str(idn/(int(len(from_points)/100)))+"%", end="\r")
        except: print("Working on point: " + str(idn))
        
        # Define the possible from and to points
        possible_from_points = determine_possible_fromto_points(edges = EDGES_ORIGINAL, point= from_point, MAX_PROJECTION=MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE=MAX_DISTANCE_OPPOSITE_EDGE)
        possible_to_points = determine_possible_fromto_points(edges = EDGES_ORIGINAL, point= to_point, MAX_PROJECTION=MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE=MAX_DISTANCE_OPPOSITE_EDGE)
        #Find the best shortest path
        SP_length_OLD, SP_edges_OLD, from_p_OLD, to_p_OLD = determine_best_shortest_path(G_original, possible_from_points=possible_from_points, possible_to_points=possible_to_points)
        if False: print("SP length in the original graph: " + str(SP_length_OLD))
        if False: plot_path(G_original_projected, from_point, to_point, SP_edges_OLD, fromto_points, mapbox_accesstoken)
        
        # Define the possible from and to points
        possible_from_points = determine_possible_fromto_points(edges = EDGES_EXTENDED, point= from_point, MAX_PROJECTION=MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE=MAX_DISTANCE_OPPOSITE_EDGE)
        possible_to_points = determine_possible_fromto_points(edges = EDGES_EXTENDED, point= to_point, MAX_PROJECTION=MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE=MAX_DISTANCE_OPPOSITE_EDGE)
        # Find the best shortest path
        SP_length_NEW, SP_edges_NEW, from_p_NEW, to_p_NEW = determine_best_shortest_path(G_extended, possible_from_points=possible_from_points, possible_to_points=possible_to_points)
        if False: print("SP length in the graph: " + str(SP_length_NEW))
        if False: plot_path(G_extended_projected, from_point, to_point, SP_edges_NEW, fromto_points, mapbox_accesstoken)
        """----------------------------------------------------------------------------------"""
        """----------------------------------------------------------------------------------"""
        idn+=1
        # Add to the dataframe
        df.loc[len(df)] = [from_point, to_point, from_p_OLD, to_p_OLD, SP_length_OLD, from_p_NEW, to_p_NEW, SP_length_NEW]
    
    # Add the length of the corresponding trajectory to this dataset
    df['Trajectory_length'] = trajectory_lengths_relevant
    
    # Only keep SPs for which we are able to compute shortest paths (e.g., both endpoints should be projectable), also remove shortest paths that have a length of zero
    df = df[(df.SP_OLD<math.inf) & (df.SP_NEW<math.inf) & (df.SP_OLD>0)]
    df['Percentage_difference'] = np.abs(((np.array(df.SP_NEW)-np.array(df.SP_OLD))/np.array(df.SP_OLD))*100)
    
    # We are only interested in shortest paths that actually differ, because this means that (part of) the extended new roads is used. 
    df = df[df.Percentage_difference > 0] 
    
    # Choose your performance metric
    # 1. MSE: np.mean((np.array(df.SP_OLD)-np.array(df.SP_NEW))**2)
    # 2. RMSE: math.sqrt(np.mean((np.array(df.SP_OLD)-np.array(df.SP_NEW))**2))
    # 3. MAE: np.mean(np.abs(np.array(df.SP_OLD)-np.array(df.SP_NEW)))
    # 4. %diff: np.mean(df.Percentage_difference)) <<<<----- USED
    metric = np.mean(df.Percentage_difference)
    
    return metric, len(df), df

