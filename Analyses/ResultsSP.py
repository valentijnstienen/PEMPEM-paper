import pandas as pd
import ast
import numpy as np
import osmnx as ox
import pickle
import shapely.wkt
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import geopandas
with open('../mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]

"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ANALYSIS -----------------------"""
"""-------------------------------------------------------------------------"""
#________________________ What to compute / show _____________________#
percentage_SPs_foundable = True
plot_projectable_points = False
average_projection_distance = True
sp_lengths = True
frequencyplots_sp_lengths_percent = True
# For metric specific settings, adjust at the relevant code box below
#_____________________________________________________________________#

#_______________________________ Load data ___________________________#
PATH_TO_SP_DIFF = "SP_diffs_30_5.csv" # csv with the shortest paths (created in RoutingResults.py)
#_____________________________________________________________________#

#_________________________ Selection settings ________________________#
CR_USED = 0 # 0, 5, 10, 20 # If start and end point are close in initial and extended graph, consider as one shortest path
import os
main_path = "/".join(os.getcwd().split("/")[:-1])
PATH_TO_SKIPS = main_path +"/Results/PEMPEM_2/SKIPS.txt" # Skips that are not in the relevant region. We ignore the numbers that represent the skips. ONLY use the SKIPS.txt file if created with unshuffled data! 
#_____________________________________________________________________#

#_________________________ Distance thresholds _______________________#
MAX_PROJECTION_DISTANCE = '30' # 30, 50, 70, 90
#_____________________________________________________________________#
"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""

# Load data
SPdiff = pd.read_csv(PATH_TO_SP_DIFF, sep = ";", index_col = 0, low_memory = False)
# Define the relevant part of the dataset
skips = ast.literal_eval(open(PATH_TO_SKIPS).readlines()[0])
skips = [i - 1 for i in skips] # Find indices
if CR_USED == 0: 
    SP_diff_relevant = SPdiff[(~SPdiff.index.isin(skips))]
else: 
    used_SPs = ast.literal_eval(open("UniqueSPs_"+str(CR_USED)+".txt").readlines()[0])
    SP_diff_relevant = SPdiff[(~SPdiff.index.isin(skips)) & SPdiff.index.isin(used_SPs)]


""" ----------------------------------------------------------------------------------------- """
""" ---------------------- FIND THE PERCENTAGE OF SPs THAT CAN BE FOUND --------------------- """
""" ----------------------------------------------------------------------------------------- """
if percentage_SPs_foundable:
    print("______________________________________________________________________________________")
    # Start with the original graph
    from_projected = SPdiff.Minimal_projection_distance_from <= int(MAX_PROJECTION_DISTANCE)
    to_projected = SPdiff.Minimal_projection_distance_to <= int(MAX_PROJECTION_DISTANCE)

    # Determine the explicit rates
    a = SP_diff_relevant.loc[from_projected & (~to_projected),:]
    b = SP_diff_relevant.loc[~(from_projected) & to_projected,:]
    c = SP_diff_relevant.loc[~(from_projected) & (~to_projected),:]
    d = SP_diff_relevant.loc[from_projected & to_projected & (SPdiff.SP_OLD == float('inf')),:]
    print("ORIGINAL graph")
    print(str(len(a)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to a from point that could not be projected.")
    print(str(len(b)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to a to point that could not be projected.")
    print(str(len(c)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to the from and end point that could not be projected.")
    print(str(len(d)/len(SP_diff_relevant)*1) + " % of the SPs can not be found because no SP exists between the projected from and end point.")
    print("----------------------------------------------------------------------------------- +")
    print(str(((len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))*1) + " % SPs for the routes can not be determined (" + str((1-(len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))*1) + " % can).")
    print()

    # Next, the extended graph
    from_projected_ext = SPdiff.Minimal_projection_distance_from_NEW <= int(MAX_PROJECTION_DISTANCE)
    to_projected_ext = SPdiff.Minimal_projection_distance_to_NEW <= int(MAX_PROJECTION_DISTANCE)

    # Determine the explicit rates
    a = SP_diff_relevant.loc[from_projected_ext & (~to_projected_ext),:]
    b = SP_diff_relevant.loc[~(from_projected_ext) & to_projected_ext,:]
    c = SP_diff_relevant.loc[~(from_projected_ext) & (~to_projected_ext),:]
    d = SP_diff_relevant.loc[from_projected_ext & to_projected_ext & (SPdiff.SP_NEW == float('inf')),:]
    print("EXTENDED graph")
    print(str(len(a)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to a from point that could not be projected.")
    print(str(len(b)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to a to point that could not be projected.")
    print(str(len(c)/len(SP_diff_relevant)*1) + " % of the SPs can not be found due to the from and end point that could not be projected.")
    print(str(len(d)/len(SP_diff_relevant)*1) + " % of the SPs can not be found because no SP exists between the projected from and end point.")
    print("----------------------------------------------------------------------------------- +")
    print(str(((len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))*1) + " % SPs for the routes can not be determined (" + str((1-(len(a)+len(b)+len(c)+len(d))/len(SP_diff_relevant))*1) + " % can).")
    print("______________________________________________________________________________________")
    print()
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ---------------------- PLOT THE POINTS THAT COULD (NOT) BE PROJECTED -------------------- """
""" ----------------------------------------------------------------------------------------- """
if plot_projectable_points:
    with open(r"graph_0-0.pickle", "rb") as input_file: G_original = pickle.load(input_file)
    crs = G_original.graph['crs']

    PLOT_POINTS = 'To' # From, To
    PLOT_GRAPH = 'OLD' # OLD, NEW

    # Project the points that should be plotted
    points = SP_diff_relevant[PLOT_POINTS].apply(lambda p: shapely.wkt.loads(p))
    gdf = geopandas.GeoDataFrame(points, geometry = points, crs= crs)
    proj_points = ox.projection.project_gdf(gdf, to_crs = crs, to_latlong = True)

    # Extract the longitudes/latitudes
    lons = proj_points.geometry.apply(lambda p: p.x)
    lats = proj_points.geometry.apply(lambda p: p.y)

    if PLOT_POINTS == 'From': 
        if PLOT_GRAPH == 'OLD': proj_p = from_projected
        else: proj_p = from_projected_ext
    else: 
        if PLOT_GRAPH == 'OLD': proj_p = to_projected
        else: proj_p = to_projected_ext

    # Find points that could be (not) projected 
    lats_proj, lats_not_proj = lats.loc[proj_p], lats.loc[~proj_p]
    lons_proj, lons_not_proj = lons.loc[proj_p], lons.loc[~proj_p]

    # Create figure
    fig = go.Figure()
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
    print("Average projection distance")
    print("-----------------------------------")
    print("Original graph")
    print("From: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.From_projected_distance < float('inf'),'From_projected_distance']))) # From points that are projected
    print("To: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.To_projected_distance < float('inf'),'To_projected_distance']))) # To points that are projected

    print("Extended graph")
    print("From: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.From_projected_distance_NEW < float('inf'),'From_projected_distance_NEW']))) # From points that are projected
    print("To: " + str(np.mean(SP_diff_relevant.loc[SP_diff_relevant.To_projected_distance_NEW < float('inf'),'To_projected_distance_NEW']))) # To points that are projected
    print("-----------------------------------")
    print()
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """


""" ----------------------------------------------------------------------------------------- """
""" ------------------------------------- SP LENGTHS ---------------------------------------- """
""" ----------------------------------------------------------------------------------------- """
if sp_lengths: 
    # Absolute average gain in SP length
    print("Average (OLD) SP length / Absolute gains in SP length")
    print(np.mean(SP_diff_relevant.loc[SP_diff_relevant.SP_OLD < float('inf'), 'SP_OLD']))
    print(np.mean(SP_diff_relevant.loc[(SP_diff_relevant.SP_OLD < float('inf')) & (SP_diff_relevant.SP_NEW < float('inf')) , 'Diff']))
    print(np.mean(SP_diff_relevant.loc[(SP_diff_relevant.SP_OLD < float('inf')), 'Diff']))
    print()
    # Gains when combining similar shortest paths
    SAME_PROJECTION = 5 #m 
    same_projection_ids = (SP_diff_relevant.Distance_between_from <= SAME_PROJECTION) & (SP_diff_relevant.Distance_between_to <= SAME_PROJECTION)

    # Absolute gain in SP length
    print("Absolute gains in SP length when merging SPs that have a start and endpoint merged ("+str(SAME_PROJECTION)+" meters)")
    print("Min diff = 0m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids,'Diff'])))
    print("Min diff = 5m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 5),'Diff'])))
    print("Min diff = 10m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 10),'Diff'])))
    print()
    # Percentage gain in SP length
    print("Percentage gains in SP length when merging SPs that have a start and endpoint merged ("+str(SAME_PROJECTION)+" meters)")
    print("Min diff = 0m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids,'Diff']/SP_diff_relevant.loc[same_projection_ids,'SP_OLD'])))
    print("Min diff = 5m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 5),'Diff']/SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 5),'SP_OLD'])))
    print("Min diff = 10m: " + str(np.mean(SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 10),'Diff']/SP_diff_relevant.loc[same_projection_ids & (SP_diff_relevant.Diff > 10),'SP_OLD'])))
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """
    

""" ----------------------------------------------------------------------------------------- """
""" ---------------------------------- FREQUENCY PLOTS -------------------------------------- """
""" ----------------------------------------------------------------------------------------- """
if frequencyplots_sp_lengths_percent:
    import matplotlib.pyplot as plt
    # Define figure
    plt.figure()
    
    # The top plot is a frequency plot of the percentage decreases
    plt.subplot(211)
    MIN_PERCENTAGE_DECREASE = 0.01
    percentage_decreases = list(SP_diff_relevant.loc[same_projection_ids,'Diff']/SP_diff_relevant.loc[same_projection_ids,'SP_OLD'])
    # Print the sorted percentage decreases
    a, b ,c = plt.hist(percentage_decreases, bins=100, range=(MIN_PERCENTAGE_DECREASE,1), density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)
    # If we want to recreate the plot in latex, save the values to a csv
    # pd.DataFrame(a).to_csv("percentage_decreases.csv")

    # The bottom plot is a frequency plot of the actual decreases
    plt.subplot(212)
    MIN_ACTUAL_DECREASE = 0 
    actual_decreases = list(SP_diff_relevant.loc[same_projection_ids,'Diff'])
    # Print the sorted actual decreases
    plt.hist(actual_decreases, bins=100, range=(MIN_ACTUAL_DECREASE,np.max(actual_decreases)), density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)

    # Show plot
    plt.show()
""" ----------------------------------------------------------------------------------------- """
""" ----------------------------------------------------------------------------------------- """

