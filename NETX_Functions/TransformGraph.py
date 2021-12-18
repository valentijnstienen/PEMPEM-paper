import pickle
import osmnx as ox
import networkx as nx
import geopandas as gp
import pandas as pd
from shapely.geometry import LineString
from NETX_Functions.PrintStuff import create_shapefile
from NETX_Functions.MathOperations import computeLengthLinestring
import pickle
import numpy as np
from copy import deepcopy

""" ----------------------------------------------------------------------------"""
""" ------------------------- Make a graph undirected  -------------------------"""
""" ----------------------------------------------------------------------------"""
def to_undirected(G):
    # Add unique ID to the edges df
    edges = ox.graph_to_gdfs(G, nodes = False)
    edges['min'] = '-' # Used as a sign, has no intrinsic value
    edges['mini'] = edges[['u','v']].min(axis=1)
    edges['maxi'] = edges[['u','v']].max(axis=1)
    edges['u'] = edges['u'].astype(str)
    edges['v'] = edges['v'].astype(str)
    # Sort the edges based on the mini and maxi variable
    edges[['mini','maxi']] = np.sort(edges[['u','v']].values)
    # Create the unique ID
    edges["period"] = edges['mini'].astype(str) + edges['min'] + edges['maxi'].astype(str) + edges['min'] + edges["key"].astype(str)  + edges['min']+ edges["length"].round(6).astype(str)
    
    
    # for j in edges.period:
    #   print(j)
    
    #print(edges[(edges.u == '211834') | (edges.v == '211834')])
    
    
    # For each edge, find the edges that occur not twice in the dataset (back and forth). Here, possible problems may arise when undirectirizing a graph
    unique_edge_IDs = list(edges.period)
    duplicates=[]
    t = 0
    for i in unique_edge_IDs:
        if unique_edge_IDs.count(i)!=2:
            duplicates.append(i)
        t +=1
    print(str(len(duplicates)) +' edges may cause problems.')
    duplicates.sort()
    # Remove the double self-edges
    for i in duplicates:
        print(i)
        z = i.split('-')
        try: u = int(z[0])
        except: u = z[0]
        try: v = int(z[1])
        except: v = z[1]
        
        if (u == v):
            try: 
                if round(G.edges[u, v, 1]['length'],6) == float(z[3]):
                    G.remove_edge(u, v, 1) 
                    #print(i)
            except:
                #print(i)
                # No reverse edge exists, do nothing
                a = 1#print("No reverse edge exists, do not do anything..")
        else: 
            # Check if there is an opposite edge 
            selected_edges = [(uu,vv,kk,e['length']) for uu,vv,kk,e in G.edges(keys = True, data=True) if (uu == v) & (vv == u) & (round(e['length'],6) == float(z[3]))]
            selected_edges = [(uu,vv,kk,e['length']) for uu,vv,kk,e in G.edges(keys = True, data=True) if (uu == v) & (vv == u)]
        
            if len(selected_edges) > 0: 
                G.remove_edge(selected_edges[0][0], selected_edges[0][1], selected_edges[0][2]) 
            else: a = 0
                #print(i)
            
            
            
    
    # Start creating the undirected graph
    graph_class = G.to_undirected_class()
   
    # deepcopy when not a view
    G_new = graph_class()
    G_new.graph.update(deepcopy(G.graph))
    G_new.add_nodes_from((n, deepcopy(d)) for n, d in G._node.items())
    
    # Add the edges to the new graph 
    G_new.add_edges_from((u, v, key, deepcopy(data)) for u, nbrs in G._adj.items() for v, keydict in nbrs.items() for key, data in keydict.items())
    return G_new
""" ----------------------------------------------------------------------------"""
#with open("Results/"+CASE+"/"+CASENAME+"/graph_0-0_ESTRADA_0609.pickle", "rb") as input_file: G = pickle.load(input_file) # Start file ESTRADA
#with open("Results/"+CASE+"/"+CASENAME+"/graph_0-0_OSM_1309.pickle", "rb") as input_file: G = pickle.load(input_file) # Start file OSM
#with open(r"Results/WorldBank/TimorLeste/30-30+75-75+10 OSM + ESTRADA/graph_0-1100.pickle", "rb") as input_file: G = pickle.load(input_file) # End file OSM (OSM + ESTRADA)
#with open(r"Results/WorldBank/TimorLeste/30-30+75-75+10 ESTRADA + OSM/graph_0-8000.pickle", "rb") as input_file: G = pickle.load(input_file) # End file ESTRADA (ESTRADA + OSM)

# TEMPORARY
#with open(r"Results/WorldBank/TimorLeste/30-30+75-75+10/graph_0-1100.pickle", "rb") as input_file: G = pickle.load(input_file) # End file ESTRADA (ESTRADA + OSM)

# nodes, edges = ox.graph_to_gdfs(G)
# print(nodes)
# print(edges)
#
# G_new = to_undirected(G)
#
# nodes, edges = ox.graph_to_gdfs(G_new)
# print(nodes)
# print(edges)

# Create and save as shapefiles
#create_shapefile(nodes, "Results/WorldBank/TimorLeste/_Shapefiles (Start)/E_nodes_1309.shp")
#create_shapefile(edges, "Results/WorldBank/TimorLeste/_Shapefiles (Start)/E_edges_1309.shp")
#create_shapefile(nodes, "Results/WorldBank/TimorLeste/_Shapefiles (Start)/O_nodes_1309.shp")
#create_shapefile(edges, "Results/WorldBank/TimorLeste/_Shapefiles (Start)/O_edges_1309.shp")
#create_shapefile(nodes, "Results/WorldBank/TimorLeste/30-30+75-75+10 ESTRADA + OSM/_Shapefiles/EO_nodes_1309.shp")
#create_shapefile(edges, "Results/WorldBank/TimorLeste/30-30+75-75+10 ESTRADA + OSM/_Shapefiles/EO_edges_1309.shp")
#create_shapefile(nodes, "Results/WorldBank/TimorLeste/30-30+75-75+10 OSM + ESTRADA/_Shapefiles/OE_nodes_1309.shp")
#create_shapefile(edges, "Results/WorldBank/TimorLeste/30-30+75-75+10 OSM + ESTRADA/_Shapefiles/OE_edges_1309.shp")
""" ----------------------------------------------------------------------------"""
""" ----------------------------------------------------------------------------"""
""" ----------------------------------------------------------------------------"""
