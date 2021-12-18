# Date       : 11-01-2021
# Environment: conda activate ox
# Location   : cd "Desktop/NETX/NETX_Functions"
# Run        : python GraphInitialization.py
# Package info: /Users/valentijnstienen/anaconda3/envs/ox/lib/python3.8/site-packages

# Load settings
#exec(open("../SETTINGS.py").read())

import geopandas as gp
import osmnx as ox
import pandas as pd
import networkx as nx
import time
import pickle
import numpy as np
import os
import glob
from pathlib import Path
import gc

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from shapely.geometry import MultiPoint, Point, Polygon, LineString

from NETX_Functions.PrintStuff import create_shapefile
from NETX_Functions.MathOperations import computeLengthLinestring
from NETX_Functions.TransformGraph import to_undirected

if CASE == 'WorldBank':
    """ ----------------------------------------------------------------------------"""
    """ ------------------ CREATE INITIAL GRAPH FOR WORLDBANK CASE ---------------- """
    """ ----------------------------------------------------------------------------"""
    network_to_be_graphed = ['OSM', 'ESTRADA']
    network_to_be_graphed.remove(case)
    network_to_be_graphed = network_to_be_graphed[0]
    """ ----------------------------------------------------------------------------"""
    """ ---------- Shapefile to GeoDF with each linestring added separately ------- """
    """ ----------------------------------------------------------------------------"""
    def segments(curve):
        return list(map(LineString, zip(curve.coords[:-1], curve.coords[1:])))
    def shape2gdf_full(p, case, make_full):
        """
        Parameters
        ----------
        p : str, File path - allowed formats geojson and ESRI Shapefile and other formats Fiona can read and write
    
        """
        # Load shapefile into GeoDataFrame. Each line piece is now in a row of this geodataframe
        gdf_old = gp.read_file(p)
        if not gdf_old.crs.is_projected: gdf_old = ox.project_gdf(gdf_old, to_crs= None, to_latlong=False)
   
        if make_full: # If the geometries in the shapefile are linestrings of complete edges, we first need to create a gdf with only the line pieces (much larger)
            gdf_old = gdf_old.dropna(subset=['geometry'])
            gdf = gdf_old.iloc[0:0]
            for i in range(0, len(gdf_old)):
                # Find the segments of the linestring
                segments_line = segments(gdf_old.loc[i,'geometry'])
                # Extract geometry
                try: old_geom = list(gdf.geometry)
                except: old_geom = []
                # Make a row for each edge piece and add the corresponding geometry
                gdf = gdf.append([gdf_old.iloc[i,:]]*len(segments_line),ignore_index=True)
                gdf.geometry = old_geom + segments_line
        else: gdf = gdf_old
        # Save new geodataframe (use pickle)
        with open("../Results/_TEMP/GraphInitialization/gdf_new_"+case+".pickle", "wb") as file: pickle.dump(gdf, file)
    """ ----------------------------------------------------------------------------"""

    """ ----------------------------------------------------------------------------"""
    """ ------------ GeoDF to Graph with each linestring added separately ----------"""
    """ ----------------------------------------------------------------------------"""
    def convert_gdf2graph(case, make_G_bidi = True):
        """
        Converts geoDF to routable networkx graph. GeoDF must have edges for each line PIECE!
    
        Parameters
        ----------
        p : str, File path - geodatafrae
        make_G_bidi : bool, if True, assumes linestrings are bidirectional
    
        Returns
        -------
        G : graph
        """
        # Load previously saved geodataframe
        with open("../Results/_TEMP/GraphInitialization/gdf_new_"+case+".pickle", "rb") as input_file: gdf = pickle.load(input_file)
    
        # Compute the start- and end-position based on linestring 
        gdf['Start_pos'] = gdf.geometry.apply(lambda x: x.coords[0])
        gdf['End_pos'] = gdf.geometry.apply(lambda x: x.coords[-1])
        gdf['length'] = [computeLengthLinestring(x, method = 'euclidean') for x in gdf['geometry']]
    
        gdf = gdf.fillna(value=np.nan)
    
        # Create Series of unique nodes and their associated position
        s_points = gdf.Start_pos.append(gdf.End_pos).reset_index(drop=True)
        s_points = s_points.drop_duplicates()
    
        # Add index of start node of linestring to geopandas DataFrame
        df_points = pd.DataFrame(s_points, columns=['Start_pos'])
        df_points['FNODE_'] = df_points.index
        gdf = pd.merge(gdf, df_points, on='Start_pos', how='inner')
    
        # Add index of end node of linestring to geopandas DataFrame
        df_points = pd.DataFrame(s_points, columns=['End_pos'])
        df_points['TNODE_'] = df_points.index
        gdf = pd.merge(gdf, df_points, on='End_pos', how='inner')

        # Bring nodes and their position in form needed for osmnx (give arbitrary osmid (index) despite not osm file)
        df_points.columns = ['pos', 'osmid']
        df_points[['x', 'y']] = df_points['pos'].apply(pd.Series)

        # Create Graph Object
        G = nx.MultiDiGraph(crs=gdf.crs)
    
        # Add nodes to graph
        df_node_xy = df_points.drop('pos', 1)
        for node, data in df_node_xy.T.to_dict().items():
            G.add_node(node, **data)
    
        attributes_edges = ['FNODE_', 'TNODE_', 'ROAD_CODE', 'ROAD_CODE_','sinuosity', 'straightdi', 'Start_pos', 'End_pos', 'osm_id', 'full_id', 'bridge', 'osm_type', 'old_name', 'layer', 'accuracy', 'name:etymo', 'email', 'descriptio', 'loc_name', 'PFM:RoadID', 'PFM:garmin', 'smoothness', 'est_width', 'lanes', 'lanes:back', 'lanes:forw', 'tracktype', 'bicycle', 'foot', 'horse', 'sac_scale', 'trail_visi', 'mtb:scale', 'ford', 'maxheight', 'motor_vehi', 'width', 'barrier', 'waterway', 'check_date', 'import', 'cutting', 'segregated', 'wheelchair', 'abandoned:', 'abandone_1', 'cycleway', 'sidewalk', 'embankment', 'lit','Observatio', 'seasonal', 'wikidata', 'ref', 'start_date', 'alt_name', 'name:en', 'mtb:scale:', 'covered', 'intermitte', 'noname', 'crossing','footway', 'bridge:str', 'official_n', 'man_made', 'incline','informal']
    
        # Add edges to graph
        for i, row  in gdf.iterrows():
            dict_row  = row.to_dict()
            if 'geometry' in dict_row: del dict_row['geometry']
            u = dict_row['FNODE_']
            v = dict_row['TNODE_']   
            for attr in attributes_edges:
                if attr in dict_row: del dict_row[attr]
            G.add_edge(u_for_edge = u, v_for_edge = v, **dict_row)
            # Add the reverse edge to the graph
            if make_G_bidi: G.add_edge(u_for_edge = v, v_for_edge = u, **dict_row)
    
        with open("../Results/_TEMP/GraphInitialization/graph_"+case+".pickle", "wb") as file: pickle.dump(G, file)
    """ ----------------------------------------------------------------------------"""

    """ ----------------------------------------------------------------------------"""
    """ -------------- Simplify the graph and add relevant attributes  -------------"""
    """ ----------------------------------------------------------------------------"""
    def create_final_initial_graph(case):
        # Load previously saved graph
        with open("../Results/_TEMP/GraphInitialization/graph_"+case+".pickle", "rb") as input_file: G = pickle.load(input_file)
    
        # Simplify graph
        G = ox.simplification.simplify_graph(G, strict=True, remove_rings=False)

        # Add edge attributes not in OSM (used in the algorithm)
        nx.set_edge_attributes(G, "-", name = 'close_to_point_start')
        nx.set_edge_attributes(G, "-", name = 'close_to_point_end')
        nx.set_edge_attributes(G, False, name = 'oneway')
        nx.set_edge_attributes(G, False, name = 'new')
    
        # Fix geometry issues for the new graph
        edges = ox.graph_to_gdfs(G, nodes = False)
        vallist = list(edges.geometry)
        nx.set_edge_attributes(G, True, "geometry")
        ind = 0
        for edge in G.edges:
            nx.set_edge_attributes(G, {edge: {'geometry': vallist[ind]}})
            ind += 1
    
        # Save the final initial graph
        if not os.path.exists("../Results/"+CASE+"/"+CASENAME): os.makedirs("../Results/"+CASE+"/"+CASENAME)
        with open("../Results/"+CASE+"/"+CASENAME+"/graph_0-0_"+case+"_1309.pickle", "wb") as file: pickle.dump(G, file)
    """ ----------------------------------------------------------------------------"""
    # Find the Graph object (NetworkX)
    if network_to_be_graphed == 'ESTRADA': shape2gdf_full('Data/'+CASE+'/_Shapefiles/roads.shp', case = 'ESTRADA', make_full = True)
    else: shape2gdf_full('Data/'+CASE+'/_Shapefiles/march22_osm_recent.shp', case = 'OSM', make_full = True)
    convert_gdf2graph(case = network_to_be_graphed, make_G_bidi = True)
    create_final_initial_graph(case = network_to_be_graphed)

    # Find the polygon object when the area is specified by a region (as a string)
    if type(area) == str: _, ch_polygon_1 = ox.graph.graph_from_place(area, simplify = True, retain_all = True, truncate_by_edge = True, clean_periphery = True)
    # Save the polygon information
    with open("Results/"+CASE+"/"+CASENAME+"/polygon_0-0.pickle", "wb") as file: pickle.dump(ch_polygon_1, file)
    with open("Results/"+CASE+"/"+CASENAME+"/PolygonInfo.txt", "w") as output: output.write(str(ch_polygon_1))
    # Plot the polygon(s) that is used
    fig = go.Figure()
    try: # when the area consists of multiple polygons
        for poly in ch_polygon_1:
            x, y = poly.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    except: # when the area is a single polygon
        x, y = ch_polygon_1.exterior.coords.xy
        fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    # Focus map on a random polygon point
    fig.update_layout(mapbox1 = dict(center = dict(lat=y[0], lon=x[0]), accesstoken = mapbox_accesstoken, zoom = 10),margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="satellite")
    # Save the map
    fig.write_html("Results/"+CASE+"/"+CASENAME+"/Visual.html")
    
    # Save the graph as shapefile  
    with open("Results/"+CASE+"/"+CASENAME+"/graph_0-0_"+network_to_be_graphed+"_1309.pickle", "rb") as input_file: G = pickle.load(input_file) #
    if two_way: G = to_undirected(G)
    nodes, edges = ox.graph_to_gdfs(G)
    if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)"): os.makedirs("Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)")
    create_shapefile(nodes, "Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)/"+network_to_be_graphed[0]+"_nodes_1309.shp")
    create_shapefile(edges, "Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)/"+network_to_be_graphed[0]+"_edges_1309.shp")
    """ ----------------------------------------------------------------------------"""   
else: # CASE == PEMPEM
    """ ----------------------------------------------------------------------------"""
    """ -------------------- CREATE INITIAL GRAPH FOR PEMPEM CASE ------------------"""
    """ ----------------------------------------------------------------------------"""
    # We start creating the initial graph using the OSMnx package. We also want to have a polygon that can be used for checking whether a GPS trace is within the scope of the case. 
    if type(area) == str: # Area is specified by a region (as a string)
        # Create initial graph
        initial_G, ch_polygon_1 = ox.graph.graph_from_place(area, simplify = True, retain_all = True, truncate_by_edge = True, clean_periphery = True)
    elif type(area[0]) == tuple: # Area is a polygon
        # Create Polygon object
        ch_polygon_1 = Polygon([Point(x) for x in area])
        # Create initial graph
        initial_G = ox.graph.graph_from_polygon(ch_polygon_1, simplify = True, retain_all = True, truncate_by_edge = True, clean_periphery = False)#,network_type = 'drive') 
    else: # Area is a rectangle
        # Define corner points of the rectangle (the area does not represent actual points)
        lu = Point(area[0], area[3])
        ld = Point(area[0], area[2])
        ru = Point(area[1], area[3])
        rd = Point(area[1], area[2])
        # Create Polygon object
        ch_polygon_1 = MultiPoint([(lu.x, lu.y), (ld.x, ld.y), (ru.x, ru.y), (rd.x, rd.y)]).convex_hull.buffer(0)
        # Create initial graph
        initial_G = ox.graph.graph_from_bbox(lu.y, ld.y, lu.x, ru.x, simplify = True, retain_all = True, truncate_by_edge = True, clean_periphery = False) #,network_type='drive')
        
    # Add edge attributes not in OSM (used in the algorithm)
    nx.set_edge_attributes(initial_G, "-", name = 'close_to_point_start')
    nx.set_edge_attributes(initial_G, "-", name = 'close_to_point_end')
    nx.set_edge_attributes(initial_G, False, name = 'new')
    nx.set_edge_attributes(initial_G, False, name = 'driven')
    nx.set_edge_attributes(initial_G, None, name = 'length_OLD')
     
    # Project the graph to the crs in which the centroid of the initial graph lies
    initial_G = ox.project_graph(initial_G, to_crs = None)
    
    for e in initial_G.edges(data = 'geometry', keys = True): 
        initial_G.edges[e[0], e[1], e[2]]['length_OLD'] = initial_G.edges[e[0], e[1], e[2]]['length']
        initial_G.edges[e[0], e[1], e[2]]['length'] = computeLengthLinestring(e[3], method = 'euclidean')
            
    # Save the graph object
    if not os.path.exists("Results/"+CASE+"/"+CASENAME): os.makedirs("Results/"+CASE+"/"+CASENAME)
    with open("Results/"+CASE+"/"+CASENAME+"/graph_0-0.pickle", "wb") as file: pickle.dump(initial_G, file)
        
    # Save the polygon information 
    with open("Results/"+CASE+"/"+CASENAME+"/polygon_0-0.pickle", "wb") as file: pickle.dump(ch_polygon_1, file)
    with open("Results/"+CASE+"/"+CASENAME+"/PolygonInfo.txt", "w") as output: output.write(str(ch_polygon_1))
    # Plot the polygon(s) that is used
    fig = go.Figure()
    try: # when the area consists of multiple polygons
        for poly in ch_polygon_1:
            x, y = poly.exterior.coords.xy
            fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    except: # when the area is a single polygon
        x, y = ch_polygon_1.exterior.coords.xy
        fig.add_trace(go.Scattermapbox(mode='lines', lat=y.tolist(), lon=x.tolist(), visible = True,  marker = {'size' : 15, 'color': 'pink', 'allowoverlap': True}))
    # Focus map on a random polygon point
    fig.update_layout(mapbox1 = dict(center = dict(lat=y[0], lon=x[0]), accesstoken = mapbox_accesstoken, zoom = 10),margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="satellite")
    # Save the map
    fig.write_html("Results/"+CASE+"/"+CASENAME+"/Visual.html")
         
    # Create and save as shapefiles
    nodes, edges = ox.graph_to_gdfs(initial_G)
    if not os.path.exists("Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)"): os.makedirs("Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)")
    create_shapefile(nodes, "Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)/start_nodes.shp")
    create_shapefile(edges, "Results/"+CASE+"/"+CASENAME+"/_Shapefiles (Start)/start_edges.shp") 
    """ ----------------------------------------------------------------------------"""