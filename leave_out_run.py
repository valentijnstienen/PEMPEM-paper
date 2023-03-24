import pandas as pd
import pickle
import osmnx as ox
import numpy as np
import ast
import time
from shapely.geometry import LineString
from multiprocessing import Pool

from mainRun import create_extended_graph
from checkPerformance import determine_greatness

"""----------- Set all the settings -----------"""
from SETTINGS import *
if not initializeGraph: area = None
if not leaveout_part: create_compare_graph_not_excluding, LO_CASE, save_shapefiles, mid_point_LO, radius_LO = None, None, None, None, None
if not plot: editing = None
GLOBAL_SETS = [SEED, shuf, CASE, CASENAME, preProcessTrajectories, PATH_TO_PRE_PROCESSED_TRAJECTORIES, (initializeGraph, area), (leaveout_part, create_compare_graph_not_excluding, \
LO_CASE, save_shapefiles, mid_point_LO, radius_LO), existing_ids, new_ids, max_dist_projection, max_bearingdiff_projection, max_dist_merge, two_way, merging_networks, max_step_input, \
dat_range, load, save, save_thresh, rest_time, viewData, do_print, (plot, editing), mapbox_accesstoken]
"""--------------------------------------------"""
    
def process_id(input_dat):
    i, x, y = input_dat
    print("Working on ID:", i, "("+str(x)+", "+str(y)+")")
    
    ################################################################################
    # 1. If you want to process specific ID(s):
    # if i not in [57, 176]:#[66, 149, 184, 84, 224, 154, 213, 296, 114, 205, 307]:
    #    return
    # 2. If you want to skip specific ID(s):
    # if i in [57, 176]:#[66, 149, 184, 84, 224, 154, 213, 296, 114, 205, 307]:
    #    return
    # 3. If you restart the process and only want to process new IDs:
    # Added to avoidd running all over again due to some stupid mistake
    # try:
    #     df_temp = pd.read_table("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/SP_df_3.csv", sep = ";")
    #     print("Already done!")
    #     return 
    # except:
    #     print("Still to be done! Continueing..")
    # 4. If you already know which IDs are relevant (no need to run the first graph) #TODO UNCOMMENT GLOBAL_SETS[9] = range(1, 14961)
    # try: 
    #     with open("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/relevant_IDs_Square_"+str(i)+".txt", "r") as f: relIds = f.readlines()[0]
    # except: 
    #     print("No IDs were relevant, not interesting at all.... continue to next square...")
    #     return [i, x, y, None, None]#continue
    # relIds = list(np.array(ast.literal_eval(relIds)))
    # GLOBAL_SETS[9] = relIds
    ################################################################################
    
    ################### Create extended graph, excluding the OSM square ##########################
    GLOBAL_SETS[7] = (True, False, "Square_"+str(i),False,(x,y),1500) # save shapefiles (last True/False)
    GLOBAL_SETS[9] = range(1, 14961)
    create_extended_graph(GLOBAL_SETS)
    with open("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/graph_0-14960_Square_"+str(i)+".pickle", "rb") as input_file: G_extended = pickle.load(input_file)
    ###############################################################################################
    
    ###############################################################################################
    # If no IDs were relevant, it does not make sense to check the compare graph, no comparison can be made
    try: 
        with open("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/relevant_IDs_Square_"+str(i)+".txt", "r") as f: relIds = f.readlines()[0]
    except: 
        print("No IDs were relevant, not interesting at all.... continue to next square...")
        return 
    ###############################################################################################
    
    ###### Create the graph while not excluding the OSM square (using only the relevant IDs) ######
    GLOBAL_SETS[7] = (True, True, "Square_"+str(i),False,(x,y),1500)
    relIds = list(np.array(ast.literal_eval(relIds)))
    GLOBAL_SETS[9] = relIds
    create_extended_graph(GLOBAL_SETS)
    with open("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/graph_Square_"+str(i)+"_compare.pickle", "rb") as input_file: G_original = pickle.load(input_file)
    ###############################################################################################
    
    ###################### Compare the two graphs based on shortest paths #########################
    MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE = 30, 5
    gm, ng, df = determine_greatness(G_original=G_original, G_extended = G_extended, IDs = relIds, MAX_PROJECTION=MAX_PROJECTION, MAX_DISTANCE_OPPOSITE_EDGE=MAX_DISTANCE_OPPOSITE_EDGE, mapbox_accesstoken=mapbox_accesstoken)
    #print("   Greatness metric (MeanPercentage):", gm)
    #print("   Number of relevant GPS trajectories:", ng)
    #print(df)
    ###############################################################################################
    
    # Save the shortest path information
    df.to_csv("Results/"+CASE+"/"+CASENAME+"/30-50+75-75+10_Square_"+str(i)+"/SP_df.csv", sep = ";")
    return
      
if __name__ == '__main__': 
    # Load all grid points
    df = pd.read_table("Data/PEMPEM/centerPoints.csv", sep = ",", usecols=['X', 'Y'])
    
    # Set up a list of all different square center points (run for all these points)
    work = []
    for i,x,y in zip(df.index, df.X, df.Y):
        work += [[i,x,y]]

    # Define how many CPUs may be used at the same time (can be slightly bigger than the 24 here), also time it
    start = time.time()
    p = Pool(30)
    results = p.map(process_id, work)
    print(time.time()-start, "seconds passed.")

    # Create the final dataframe that contains all information for all different squares
    df_new = pd.DataFrame(columns= ['Square', 'From', 'To', 'Trajectory_length', 'SP_OLD', 'SP_NEW', 'Percentage_difference'])
    for i in range(0, 308):
        print("Processing square:", i)
        try:
            df = pd.read_table("Results/PEMPEM_2 (DatVel)/LO_CASES/30-50+75-75+10_Square_"+str(i)+"/SP_df.csv", sep = ";", index_col = 0)
            df.reset_index(drop = True, inplace = True)
        except:
            print("Continue.. this id has no data..")
            continue
        if len(df) < 1:
            print("Continue.. this id has no data..")
            continue
        for j in range(len(df)):
            df_new.loc[len(df_new)] = [i] + list(df.loc[j, ['From', 'To', 'Trajectory_length', 'SP_OLD', 'SP_NEW', 'Percentage_difference']])
    df_new.to_csv("df_final_FULL.csv", sep = ";")
    
