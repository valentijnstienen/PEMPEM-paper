import pandas as pd
import ast
import numpy as np
import osmnx as ox
import pickle
import shapely.wkt
import geopandas as gpd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import geopandas
import os
import matplotlib.pyplot as plt
from shapely.geometry import Point

with open('../mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]

"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ANALYSIS -----------------------"""
"""-------------------------------------------------------------------------"""
#________________________ What to compute / show _____________________#
percentage_SPs_foundable = False
plot_projectable_points = False
if plot_projectable_points: 
    main_path = "/".join(os.getcwd().split("/")[:-1])
    PATH_TO_GRAPH = main_path +"/Results/PEMPEM/PEMPEM_FINAL/graph_0-0.pickle"
average_projection_distance = False
sp_lengths = True
frequencyplots_sp_lengths_percent = False
if frequencyplots_sp_lengths_percent: save_percentages = True
# For metric specific settings, adjust at the relevant code box below
#_____________________________________________________________________#

#_______________________________ Load data ___________________________#
MAX_PROJECTION_DISTANCE = '30' # 30, 50, 70, 90
PATH_TO_SP_DIFF = "RoutingResults/SP_diffs_INITIAL_30_5.csv" # csv with the shortest paths (created in RoutingResults.py)
if sp_lengths | frequencyplots_sp_lengths_percent: PATH_TO_SECOND_SP_DIFF = "RoutingResults/SP_diffs_CASE00_30_5.csv"
#_____________________________________________________________________#

#_________________________ Selection settings ________________________#
CLOSENESSRADIUS = 0
#CR_USED = 0 # 0, 5, 10, 20 # If start and end point are close in initial and extended graph, consider as one shortest path
main_path = "/".join(os.getcwd().split("/")[:-1])
PATH_TO_SKIPS = main_path +"/Results/PEMPEM/SKIPS.txt" # Skips that are not in the relevant region. We ignore the numbers that represent the skips. ONLY use the SKIPS.txt file if created with unshuffled data! 
#_____________________________________________________________________#

"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""

# Load data
SPdiff = pd.read_csv(PATH_TO_SP_DIFF, sep = ";", index_col = 0, low_memory = False)
for c in ['From', 'To']:
    SPdiff[c] = SPdiff[c].apply(shapely.wkt.loads)
if sp_lengths | frequencyplots_sp_lengths_percent: 
    SPdiff_2 = pd.read_csv(PATH_TO_SECOND_SP_DIFF, sep = ";", index_col = 0, low_memory = False)
    for c in ['From', 'To']:
        SPdiff_2[c] = SPdiff_2[c].apply(shapely.wkt.loads)
  
# Define the relevant part of the dataset
skips = ast.literal_eval(open(PATH_TO_SKIPS).readlines()[0])
skips = [i - 1 for i in skips] # Find indices
 
def find_unique_ids(df, CR):
    unique_SPs = [0]
    ind = 0
    from_points = df.From
    to_points = df.To
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
            if (dist_from <= CR) & (dist_to <= CR):
                add = False
                break
        if add:
            unique_SPs += [ind]
        ind+=1
    # Save unique OD pairs
    with open("UniqueSPs_"+str(CR)+".txt", "w") as output: output.write(str(unique_SPs))
    return unique_SPs

if CLOSENESSRADIUS == 0: 
    SP_diff_relevant = SPdiff[(~SPdiff.index.isin(skips))].reset_index(drop=True)
    if sp_lengths | frequencyplots_sp_lengths_percent: SP_diff_relevant_2 = SPdiff_2[(~SPdiff_2.index.isin(skips))].reset_index(drop=True)
else: 
    try: used_SPs = ast.literal_eval(open("UniqueSPs_"+str(CLOSENESSRADIUS)+".txt").readlines()[0])
    except: used_SPs = find_unique_ids(df = SPdiff, CR = CLOSENESSRADIUS)
    SP_diff_relevant = SPdiff[(~SPdiff.index.isin(skips)) & SPdiff.index.isin(used_SPs)].reset_index(drop=True)
    if sp_lengths | frequencyplots_sp_lengths_percent: SP_diff_relevant_2 = SPdiff_2[(~SPdiff_2.index.isin(skips)) & SPdiff_2.index.isin(used_SPs)].reset_index(drop=True)


print("Amount of shortest paths considered: " + str(len(SP_diff_relevant)))

""" ----------------------------------------------------------------------------------------- """
""" ---------------------- FIND THE PERCENTAGE OF SPs THAT CAN BE FOUND --------------------- """
""" ----------------------------------------------------------------------------------------- """
if percentage_SPs_foundable:
    print("______________________________________________________________________________________")
    print("Percentage of points that can be projected")
    # Start with the original graph
    from_projected = SP_diff_relevant.Minimal_projection_distance_from <= int(MAX_PROJECTION_DISTANCE)
    to_projected = SP_diff_relevant.Minimal_projection_distance_to <= int(MAX_PROJECTION_DISTANCE)

    # Determine the explicit rates
    a = SP_diff_relevant.loc[from_projected & (~to_projected),:]
    b = SP_diff_relevant.loc[~(from_projected) & to_projected,:]
    c = SP_diff_relevant.loc[~(from_projected) & (~to_projected),:]
    d = SP_diff_relevant.loc[from_projected & to_projected & (SP_diff_relevant.SP == float('inf')),:]
    print(str(len(a)/len(SP_diff_relevant)) + " % of the SPs can not be found due to a from point that could not be projected.")
    print(str(len(b)/len(SP_diff_relevant)) + " % of the SPs can not be found due to a to point that could not be projected.")
    print(str(len(c)/len(SP_diff_relevant)) + " % of the SPs can not be found due to the from and end point that could not be projected.")
    print(str(len(d)/len(SP_diff_relevant)) + " % of the SPs can not be found because no SP exists between the projected from and end point.")
    print("----------------------------------------------------------------------------------- +")
    print(str(((len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))) + " % SPs for the routes can not be determined (" + str((1-(len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))) + " % can).")
    print("______________________________________________________________________________________")
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ---------------------- PLOT THE POINTS THAT COULD (NOT) BE PROJECTED -------------------- """
""" ----------------------------------------------------------------------------------------- """
if plot_projectable_points:
    with open(PATH_TO_GRAPH, "rb") as input_file: G_original = pickle.load(input_file)
    crs = G_original.graph['crs']

    PLOT_POINTS = ['From','To'] # From, To 
    try: from_projected
    except:
        from_projected = SP_diff_relevant.Minimal_projection_distance_from <= int(MAX_PROJECTION_DISTANCE)
        to_projected = SP_diff_relevant.Minimal_projection_distance_to <= int(MAX_PROJECTION_DISTANCE)

    # Create figure
    fig = go.Figure()
    
    for case in PLOT_POINTS:
        # Project the points that should be plotted
        points = SP_diff_relevant[case]
        gdf = geopandas.GeoDataFrame(points, geometry = points, crs= crs)
        proj_points = ox.projection.project_gdf(gdf, to_crs = crs, to_latlong = True)
    
        # Extract the longitudes/latitudes
        lons = proj_points.geometry.apply(lambda p: p.x)
        lats = proj_points.geometry.apply(lambda p: p.y)

        if case == 'From': proj_p = from_projected
        else: proj_p = to_projected
            
        # Find points that could be (not) projected 
        lats_proj, lats_not_proj = lats.loc[proj_p], lats.loc[~proj_p]
        lons_proj, lons_not_proj = lons.loc[proj_p], lons.loc[~proj_p]

        fig.update_layout(mapbox1 = dict(center = dict(lat=lats.mean(), lon=lons.mean()), accesstoken = mapbox_accesstoken, zoom = 13), margin = dict(t=10, b=0, l=10, r=10),showlegend=False,mapbox_style="light")
        fig.add_trace(go.Scattermapbox(mode='markers', lat=lats_not_proj, lon=lons_not_proj, visible = True, text = 'Index: ' + lats_not_proj.index.astype(str), marker = {'size' : 10, 'opacity': 1, 'color': 'red', 'allowoverlap': True}))
        fig.add_trace(go.Scattermapbox(mode='markers', lat=lats_proj, lon=lons_proj, visible = True, text = 'Index: ' + lats_proj.index.astype(str), marker = {'size' : 10, 'opacity': 1, 'color': 'green', 'allowoverlap': True}))

    # Launch app
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id = 'fig2', children=[dcc.Graph(id='fig',figure=fig, style={"height" : "95vh"})], style={"height" : "80vh"})], className = "container" )
    if __name__ == '__main__':
        app.run_server(debug=False)
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ------------------------------ AVERAGE PROJECTION DISTANCE ------------------------------ """
""" ----------------------------------------------------------------------------------------- """
if average_projection_distance:
    print("Average projection distance (when projected)")
    print("-----------------------------------")
    print("Original graph")
    print("From: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.From_projected_distance < float('inf'),'From_projected_distance']))) # From points that are projected
    print("To: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.To_projected_distance < float('inf'),'To_projected_distance']))) # To points that are projected
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ------------------------------------- SP LENGTHS ---------------------------------------- """
""" ----------------------------------------------------------------------------------------- """
if sp_lengths:
    # Absolute average gain in SP length
    print("Average SP length")
    print("Graph 1: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.SP < float('inf'), 'SP'])))
    print("Graph 2: " + str(np.mean(SP_diff_relevant_2.loc[SP_diff_relevant_2.SP < float('inf'), 'SP'])))
    
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ---------------------------------- FREQUENCY PLOTS -------------------------------------- """
""" ----------------------------------------------------------------------------------------- """
def pairwise_distance_between_cols(column_1, column_2):
    column_3 = []
    for i, j in zip(column_1, column_2):
        try: 
            point_1 = Point(ast.literal_eval(i))
            point_2 = Point(ast.literal_eval(j))
            dist = point_1.distance(point_2)
        except: 
            dist = float('inf')
        column_3.append(dist)
    return column_3
if frequencyplots_sp_lengths_percent:
    # Find distances between the projected points
    distances_between_from = pairwise_distance_between_cols(SP_diff_relevant.From_projected, SP_diff_relevant_2.From_projected)
    distances_between_to = pairwise_distance_between_cols(SP_diff_relevant.To_projected, SP_diff_relevant_2.To_projected)
    diff_in_SP = SP_diff_relevant.SP - SP_diff_relevant_2.SP

    # Look at the shortest paths that have thier points projected at the same spot. We can only compare the lenghts of these shortest paths...
    SAME_PROJECTION = 5 #m 
    same_projection_ids = list(np.where((np.array(distances_between_from) <= SAME_PROJECTION) & (np.array(distances_between_to) <= SAME_PROJECTION))[0])
    
    # Define figure
    plt.figure()
    
    # The top plot is a frequency plot of the percentage decreases
    plt.subplot(211)
    plt.title("Percentage decreases")
    MIN_PERCENTAGE_DECREASE = 0.01 #1%
    percentage_decreases = list(diff_in_SP[same_projection_ids]/SP_diff_relevant.loc[same_projection_ids,'SP'])

    # Print the sorted percentage decreases
    a, b, c = plt.hist(percentage_decreases, bins=100, range=[MIN_PERCENTAGE_DECREASE, max(percentage_decreases)], density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)
    # If we want to recreate the plot in latex, save the values to a csv
    if save_percentages: pd.DataFrame(a).to_csv("percentage_decreases.csv")

    # The bottom plot is a frequency plot of the actual decreases
    plt.subplot(212)
    plt.title("Actual decreases")
    MIN_ACTUAL_DECREASE = 10
    actual_decreases = list(diff_in_SP[same_projection_ids])
    # Print the sorted actual decreases
    plt.hist(actual_decreases, bins=100, range=[MIN_ACTUAL_DECREASE,max(actual_decreases)], density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)

    # Show plot
    plt.show()
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """

