"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ANALYSIS -----------------------"""
"""-------------------------------------------------------------------------"""
#_______________________ Initial/Extended graphs _____________________#
import os
main_path = "/".join(os.getcwd().split("/")[:-1])
PATH_TO_GRAPH = main_path +"/Results/PEMPEM/PEMPEM_FINAL/graph_0-0.pickle" #"/Results/PEMPEM/PEMPEM_FINAL/30-50+75-75+10_CASE00/graph_0-14960.pickle"
CASENAME = "INITIAL"
#_____________________________________________________________________#

#______________________________ OD pairs _____________________________#
PATH_TO_FROMTO_COMBINATIONS = main_path+"/Data/PEMPEM/PEMPEM_stops_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv"
#_____________________________________________________________________#

#________________________ Distance thresholds ________________________#
MAX_PROJECTION = 70 # 30, 50, 70, 90
MAX_DISTANCE_OPPOSITE_EDGE = 5
#_____________________________________________________________________#

#_________________________ Selection settings ________________________#
SELECTION = None # None, means all OD pairs in PATH_TO_FROMTO_COMBINATIONS
PLOTPATH = False # Recommendation: only use when 1 ID selected
#_____________________________________________________________________#

#__________________________ Savings settings _________________________#
FNAME = "SP_diffs_"+CASENAME+"_"+str(MAX_PROJECTION)+"_"+str(MAX_DISTANCE_OPPOSITE_EDGE)+".csv"
#_____________________________________________________________________#

#________________________ Mapbox accesstoken _________________________#
with open('../mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]
#_____________________________________________________________________#
"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""