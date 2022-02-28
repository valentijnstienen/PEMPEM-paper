# Date       : 11-01-2021
# Environment: conda activate ox
# Location   : cd "Desktop/NETX"
# Run        : python mainRun.py
# Package info: /Users/valentijnstienen/anaconda3/envs/ox/lib/python3.8/site-packages

# Load settings
exec(open("./SETTINGS.py").read())

import osmnx as ox
import pandas as pd
import time
import pickle
import os
import glob
import gc
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from shapely.geometry import Point, Polygon
from pathlib import Path

#from LoadDataOSM import LoadData_speed
from NETX_Functions.PrintStuff import addGraph, addEdge, create_shapefile
from NETX_Functions.algorithm import ExtendGraph, ExtendGraph_trajectory, ExtendGraphWithOSM_NEW
from NETX_Functions.TransformGraph import to_undirected

# Set seed
random.seed(SEED)

# Garbage collector
gc.collect()

################################################################################################################################################################
##################################################################### PREPROCESSING ############################################################################
################################################################################################################################################################

""" ---------------------------------------------------------------------------------"""
""" ------------------------------ PreProcess Data ----------------------------------"""
""" ---------------------------------------------------------------------------------"""
if preProcessTrajectories: exec(open("Data/CreateTraces_Preprocessing.py").read())
""" ---------------------------------------------------------------------------------"""

""" ---------------------------------------------------------------------------------"""
""" -------------- Load the pre-processed GPS trajectories (GPS traces) -------------"""
""" ---------------------------------------------------------------------------------"""
# Load complete dataset
points = pd.read_csv(PATH_TO_PRE_PROCESSED_TRAJECTORIES, sep = ";", index_col = 0, low_memory=False)
""" -------------------------------- Shuffle Data -----------------------------------"""
counts = list(points['ID'].value_counts().sort_index(axis = 0))
ids = list(points['ID'].unique())
if shuf:
    random.shuffle(ids)
    l, ind = [], 0
    for i in ids:
        l += [i]*counts[ind]
        ind+=1
    points['ID'] = l
""" ---------------------------------------------------------------------------------"""
# Find specific part of data that is used.
points = points[points["ID"].isin(new_ids)]
""" ---------------------------------------------------------------------------------"""

# If you want to view the data: Result saved in _DataViews
if viewData: 
    # Create a figure
    fig = go.Figure()
    # Draw basemap (OSM)
    fig.update_layout(mapbox1 = dict(center = dict(lat=points.Latitude.mean(), lon=points.Longitude.mean()), accesstoken = mapbox_accesstoken, zoom = 13),margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="satellite")
    fig.add_trace(go.Scattermapbox(mode='markers', lat=points.Latitude, lon=points.Longitude, visible = True, text = 'ID: ' + points.ID.astype(str), marker = {'size' : 10, 'opacity': 1, 'color': 'pink', 'allowoverlap': True}))
    # Save the map
    if not os.path.exists("Results/"+CASE+"/_DataViews/"): os.makedirs("Results/"+CASE+"/_DataViews/")
    fig.write_html("Results/"+CASE+"/_DataViews/" + str(new_ids) + ".html")

""" ---------------------------------------------------------------------------------"""
""" -------------------------------- Initialize graph -------------------------------"""
""" ---------------------------------------------------------------------------------"""
if initializeGraph: exec(open("NETX_Functions/GraphInitialization.py").read())
""" ---------------------------------------------------------------------------------"""

# Save settings for the algorithm, the last setting will change per ID iteration, for now, set it equal to None
settings = [max_dist_projection, max_bearingdiff_projection, max_dist_merge, two_way, None, merging_networks]

# Define settings string (used for saving)
set_string = ""
for lst in settings[0:2]: set_string = set_string + '-'.join(str(e) for e in lst) + "+"
set_string = set_string + str(settings[2])

# Find the unique IDs that should be incorporated
uniqueIDs = points.ID.unique()

# Adjust start of existing_ids to the ones that are actually in the dataset. Add the initial graph to the possible ids (to be able to load it)
if existing_ids != [0]: existing_ids = [0] + [existing_ids[-1]]

""" ---------------------------------------------------------------------------------"""
""" ----------------------------- Load the initial graph ----------------------------"""
""" ---------------------------------------------------------------------------------"""
if (len(existing_ids) == 1) & (existing_ids[0] == 0):
    # Load data
    with open(r"Results/"+CASE+"/"+CASENAME+"/graph_0-0.pickle", "rb") as input_file: G = pickle.load(input_file) 
    with open(r"Results/"+CASE+"/"+CASENAME+"/polygon_0-0.pickle", "rb") as input_file: ch_polygon_1 = pickle.load(input_file) # Load polygon

    # Remove all old graphs/polygons
    for f in Path('Results/'+CASE+'/'+CASENAME+'/'+ set_string).glob('*.pickle'):
        try: f.unlink()
        except OSError as e: print("Error: %s : %s" % (f, e.strerror))
else:
    with open(r"Results/"+CASE+"/"+CASENAME+"/" + set_string + "/graph_"   + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "rb") as input_file: G = pickle.load(input_file)
    with open(r"Results/"+CASE+"/"+CASENAME+"/" + set_string + "/polygon_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "rb") as input_file: ch_polygon_1 = pickle.load(input_file)

# Define the coordinate reference system used throughout the algorithm
used_crs = G.graph["crs"]
print("initial_G loaded.... CRS: " + str(used_crs))   
""" ---------------------------------------------------------------------------------"""

################################################################################################################################################################
####################################################################### ALGORITHM ##############################################################################
################################################################################################################################################################

# Measure runtime
start = time.time()

# Initialize parameters
errors, skips, trips = [], [], []

for new_id in new_ids:
    print("Adding ID " + str(new_id) + " to the road network.")
    
    # Skip IDs that do not exist. 
    if new_id not in uniqueIDs: continue

    # Extract relevant points
    points_new = points[points["ID"].isin([new_id])].reset_index(drop = True)
    
    # If only part of the points_new must be examined
    if dat_range is not None: points_new = points_new.iloc[dat_range,:].reset_index(drop = True)

    # If the new graph is (partly) outside the region covered by the existing graph, extend this existing graph with the OSM graph in the new region. Also, determine the used_polygon.
    # Currently, polygon_extended is just the existing polygon (ch_polygon_1), as we do not extend OSM maps during the algorithm. Used_polygon is a small polygon that covers the points 
    # in [points_new] with a buffer.
    polygon_extended, _ , used_polygon = ExtendGraphWithOSM_NEW(used_crs, ch_polygon_1, points_new)
    
    # If the [used_polygon] is not in the current overlapping polygon, skip this ID
    if used_polygon is None:
        print("This ID contains points outside the considered region. Therefore, it is skipped. Saved to file.. ")
        # Save the skips to a separate file (for later reference)
        skips += [new_id]
        with open("SKIPS.txt", "w") as output: output.write(str(skips))
        # Add the id to the existing IDs for saving purposes
        existing_ids = existing_ids + [new_id]
        if save & ((new_id+1) % save_thresh == 0):
            if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string)
            with open("Results/"+CASE+"/"+CASENAME+"/" + set_string + "/graph_"   + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(G, file)
            with open("Results/"+CASE+"/"+CASENAME+"/" + set_string + "/polygon_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(polygon_extended, file)
        continue

    # For the final setting, we include information about the subgraph that is considered based on the used_polygon. (speeds up the computation time)
    if len(G.edges) > 0:
        # Classify the edges of the new graph that are within the ch_polygon, set these equal to True (reset each time)
        nodes, edges = ox.graph_to_gdfs(G, nodes = True, node_geometry = True)
        edges_used = edges[edges.intersects(used_polygon) | edges.within(used_polygon)]
        nodes_used_extended = list(set(list(edges_used.u) + list(edges_used.v)))
    else: nodes_used_extended = [] # Could happen, for instance, when starting with an empty graph
    
    # Set the final settings parameter (specifies which subgraph is relevant)
    settings[4] = [nodes_used_extended[:], list(G.nodes)[:], used_polygon]

    # If you want to save the IDs that are being added on the fly
    # trips += [new_id]
    # with open("TRIPS.txt", "w") as output: output.write(str(trips))
    
    ################################## EXTEND THE GRAPH #######################################
    ExtendGraph(G, points_new, settings, MAX_STEP_INPUT = max_step_input, do_print = do_print)  
    #except: # Keep track of errors
    #     G = initial_G_extended
    #     print("Graph could not be extended. Error saved to file.. ")
    #     errors += [new_id]
    #     with open("ERRORS.txt", "w") as output:
    #         output.write(str(errors))
    ###########################################################################################
    
    # Extend the existing_ids with the now added [new_id]. Necessary for loading the right data if needed
    existing_ids = existing_ids + [new_id]
    
    # Save the graph and polygon for while running (potential error backup files)
    if save & ((new_id+1) % save_thresh == 0):
        if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string)
        with open("Results/"+CASE+"/"+CASENAME+"/"+set_string +"/graph_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(G, file)
        with open("Results/"+CASE+"/"+CASENAME+"/"+set_string +"/polygon_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(polygon_extended, file)
        time.sleep(rest_time)


################################################################################################################################################################
###################################################################### SAVING FILES ############################################################################
################################################################################################################################################################
# Save the final graph (note that this may be a double save if latest new_id was saved due to [save_thresh])
if save & (len(new_ids) > 0):
    if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string)
    with open("Results/"+CASE+"/"+CASENAME+"/"+set_string +"/graph_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(G, file)
    with open("Results/"+CASE+"/"+CASENAME+"/"+set_string +"/polygon_" + str(existing_ids[0]) + "-"+ str(str(existing_ids[len(existing_ids)-1])) + ".pickle", "wb") as file: pickle.dump(polygon_extended, file)

# Project the final graph back to lon/lats
G = ox.project_graph(G, to_crs='epsg:4326') 

# Print and save the graph
if two_way: G = to_undirected(G)
nodes, edges = ox.graph_to_gdfs(G)

# Save the nodes/edges as csv files
if save: 
    if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Graphs"): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Graphs")
    nodes.to_csv("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Graphs/Nodes_"+ str(existing_ids[0]) + "_"+ str(str(existing_ids[len(existing_ids)-1]))+".csv", sep = ";")
    edges.to_csv("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Graphs/Edges_"+ str(existing_ids[0]) + "_"+ str(str(existing_ids[len(existing_ids)-1]))+".csv", sep = ";")

# Create and save as shapefiles
if save: 
    if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Shapefiles"): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Shapefiles")
    create_shapefile(nodes, "Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Shapefiles/SF_nodes.shp")
    create_shapefile(edges, "Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_Shapefiles/SF_edges.shp")

# Print the runtime
print(str(time.time() - start) + " seconds have passed.")

################################################################################################################################################################
##################################################################### START PLOTTING ###########################################################################
################################################################################################################################################################
if plot: 
    # Create figure
    fig = go.Figure()
    
    # If we want to save/plot an existing graph (without running the algorithm)
    if len(new_ids) == 0: points_new = points[points["ID"].isin(existing_ids)].reset_index(drop = True)

    # Draw basemap (OSM)
    fig.update_layout(mapbox1 = dict(center = dict(lat=points_new.Latitude.mean(), lon=points_new.Longitude.mean()), accesstoken = mapbox_accesstoken, zoom = 13), margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="light") # or use satellite as mapbox_style

    # Draw the graph
    # If we are editing, only draw the relevant piece (that corresponds to the ID) to the map
    if editing & (len(new_ids) > 0):
        # Determine the used_polygon. If necessary, adjust the buffer here. 
        used_polygon = ox.projection.project_geometry(used_polygon.buffer(0), crs = used_crs,  to_latlong = True)[0]
        # Find all nodes and edges that are within this polygon. These will all be visualized
        edges_used = edges[edges.intersects(used_polygon) | edges.within(used_polygon)]
        nodes_used_extended = list(set(list(edges_used.u) + list(edges_used.v) + list(nodes[nodes.within(used_polygon)].index)))

        # Plot the subgraph
        if len(edges_used) > 0: fig = addGraph(fig, G.subgraph(nodes_used_extended), ['red', 'red'], include_existing = True)
        else: # If there are no edges in the subgraph, only plot the nodes
            fig = addGraph(fig, G.subgraph(nodes_used_extended), ['red', 'red'], include_existing = True, only_nodes = True)
    else: # if we are not editing, we might want to plot the complete final results, i.e., the whole graph. 
        fig = addGraph(fig, G, ['red', 'red'], include_existing = True)

    # Save the map
    if save: 
        if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_HTMLs"): os.makedirs("Results/"+CASE+"/"+CASENAME+"/"+set_string+"/_HTMLs")
        fig.write_html("Results/"+CASE+"/"+CASENAME+"/"+set_string +"/_HTMLs/" + str(existing_ids[0]) + "_"+ str(str(existing_ids[len(existing_ids)-1])) + ".html")

    # If we are editing and there is at least one new ID, we plot the GPS points corresponding to the new IDs. Note that we do not want to save these dots in the saved map.
    if editing & (len(new_ids) > 0): 
        fig.add_trace(go.Scattermapbox(mode='markers', lat=points_new.Latitude, lon=points_new.Longitude, visible = True, text = 'Index: ' + points_new.index.astype(str)+ ', Course: '+points_new['Course'].astype(str), marker = {'size' : 10, 'opacity': 1, 'color': 'pink', 'allowoverlap': True}))

    ############################################################ HIGHLIGHT AN EDGE (NOT TESTED YET) ################################################################
    #fig = addEdge(fig, G.edges[5058403764, '6478308699/Node_p: 26_5_2', 0])
    ################################################################################################################################################################

    ################################################################ ADD PROJ_POINT OF AN EDGE (RED) ###############################################################
    #proj_point = ox.projection.project_geometry(Point(226958.4623659053, -75473.67194116105), crs = used_crs,to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[proj_point.y], lon=[proj_point.x], visible = True, text = "Projection", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    ################################################################################################################################################################

    ########################################################## ADD CLOSE_TO_POINT OF AN EDGE (YELLOW) ##############################################################
    #close_to_point = ox.projection.project_geometry(Point(199895.39323496912, -75395.90744521764), crs = used_crs,to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[close_to_point.y], lon=[close_to_point.x], visible = True, text = "CP", marker = {'size' : 15, 'opacity': 1, 'color': 'yellow', 'allowoverlap': True}))
    #close_to_point = ox.projection.project_geometry(Point(896180.5304834486, -84031.05057362781), crs = used_crs,to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[close_to_point.y], lon=[close_to_point.x], visible = True, text = "CP", marker = {'size' : 15, 'opacity': 1, 'color': 'yellow', 'allowoverlap': True}))
    ################################################################################################################################################################

    ############################################################### ADD RANDOM POINTS (LON/LAT) ####################################################################
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[-0.70872], lon=[102.425], visible = True, text = "1", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[-0.681575], lon=[102.502435], visible = True, text = "2", marker = {'size' : 15, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
    ################################################################################################################################################################

    ################################################################ SHORTEST PATH (START/END POINT) ###############################################################
    #start_point = ox.projection.project_geometry(Point(233351.93859594292, -88896.90829905252), crs = used_crs, to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[start_point.y], lon=[start_point.x], visible = True, text = "Start", marker = {'size' : 15, 'opacity': 1, 'color': 'green', 'allowoverlap': True}))
    #end_point = ox.projection.project_geometry(Point(233379.80118036323, -88934.50533398885), crs = used_crs, to_latlong=True)[0]
    #fig.add_trace(go.Scattermapbox(mode='markers', lat=[end_point.y], lon=[end_point.x], visible = True, text = "End", marker = {'size' : 15, 'opacity': 1, 'color': 'green', 'allowoverlap': True}))
    ################################################################################################################################################################
    
    ############################################################################ POLYGONS ##########################################################################
    try:
        for poly in used_polygon: #[]
            x, y = poly.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    except:
        for poly in [used_polygon]: #[]
            x, y = poly.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    ################################################################################################################################################################

    # Launch app
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id = 'fig2', children=[dcc.Graph(id='fig',figure=fig, style={"height" : "95vh"})], style={"height" : "80vh"})], className = "container" )
    if __name__ == '__main__':
        app.run_server(debug=False)

