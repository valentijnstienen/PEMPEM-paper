"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ANALYSIS -----------------------"""
"""-------------------------------------------------------------------------"""
#_______________________ Initial/Extended graphs _____________________#
import os
main_path = "/".join(os.getcwd().split("/")[:-1])
PATH_TO_INITIAL_GRAPH = main_path +"/Results/PEMPEM_2/PEMPEM_0228/graph_0-0.pickle"
PATH_TO_EXTENDED_GRAPH = main_path +"/Results/PEMPEM_2/PEMPEM_0228/30-30+75-75+10/graph_0-2.pickle"
#_____________________________________________________________________#

#______________________________ OD pairs _____________________________#
PATH_TO_FROMTO_COMBINATIONS = main_path+"/Data/PEMPEM/PEMPEM_stops_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv"
#_____________________________________________________________________#

#__________________________ Uniqueness / CR __________________________#
FIND_UNIQUE_ODS = False
if FIND_UNIQUE_ODS: CLOSENESSRADIUS = 20
#_____________________________________________________________________#

#________________________ Distance thresholds ________________________#
MAX_PROJECTION = 30 # 30, 50, 70, 90
MAX_DISTANCE_OPPOSITE_EDGE = 5
#_____________________________________________________________________#

#_________________________ Selection settings ________________________#
SELECTION = None # None, means all OD pairs in PATH_TO_FROMTO_COMBINATIONS
PLOTPATH = False # Recommendation: only use when 1 ID selected
#_____________________________________________________________________#

#__________________________ Savings settings _________________________#
FNAME = "SP_diffs_"+str(MAX_PROJECTION)+"_"+str(MAX_DISTANCE_OPPOSITE_EDGE)+".csv"
#_____________________________________________________________________#

#________________________ Mapbox accesstoken _________________________#
with open('../mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]
#_____________________________________________________________________#
"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""