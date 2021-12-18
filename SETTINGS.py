"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ALGORITHM ----------------------"""
"""-------------------------------------------------------------------------"""
SEED = 0
shuf = False
#____________________________ Define Case ____________________________#
CASE = "PEMPEM" #"WorldBank" #"PEMPEM" #TODO WORLDBANK
if CASE == "WorldBank": case = 'OSM'# ESTRADA # Which network used as trajectory data #TODO WORLDBANK
CASENAME = "SMALL_0211" #"TimorLeste_EO"/"SMALL" #TODO WORLDBANK 
# ____________________________________________________________________#
preProcessTrajectories = False
initializeGraph = False
#____________________________ Define Area ____________________________#
"""
Use one of the following formats:
- a region defined by a string (e.g., "timor leste") 
- a rectangle defined by a list with the form [lon_min, lon_max, lat_min, lat_max] (e.g., [101.85, 102.99, -1.04, -0.18])
- a polygon defined by a list of points. (e.g.,: [(101.91454,-0.46966), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)])

Use cases
- PEMPEM (small): [(101.91454,-0.46966), (102.3965,-0.1993), (102.83846,-0.36753), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)]
- WorldBank: "timor leste"
""" 
area =  [(101.91454,-0.46966), (102.3965,-0.1993), (102.83846,-0.36753), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)] #[101.85, 102.99, -1.04, -0.18] #TODO What if no idea of size poolygon, use the information in the data_used.
# ____________________________________________________________________#

#__________________ Scope Settings for th[e algorithm _________________#
existing_ids = [0]#
new_ids = range(1, 14961)#range(5000, 8000)#range(5400, 14961)#range(9000, 9999)#range(12000,14961)#range(10000,12000)#range(11600,14859)#range(8100,8135)#range(1, 14859) range(1,1137) # 8001 # 1101
# ____________________________________________________________________#

#______________ Mathematical Settings for the algorithm ______________#
max_dist_projection = [30, 50]# #\bar{d},\bar{\bar{d}} #TODO WORLDBANK     [30, 30] # [30, 50]           
max_bearingdiff_projection = [75, 75] #\bar{alpha},\bar{\bar{alpha}}    
max_dist_merge = 10 #meters
two_way = False #TODO WORLDBANK
merging_networks = False #TODO WORLDBANK
# ____________________________________________________________________#
# ____________________________________________________________________#


# ____________________________________________________________________#
#____________ Data limitation (only use in single new_id) ____________#
max_step_input = None # Maximum number of points examined within one ID
dat_range = None# range(531, 536) # Range that specifies the scope of the data (e.g., 245:345)
# ____________________________________________________________________#

#___________________________ Save settings ___________________________#
load = True # True if you want to load the graph corresponding to the existing ids
save = True # True if you want to save the graphs/polygons during the run. (RECOMMENDED)
save_thresh = 100# Save the graph once every [save_thresh] IDs #TODO WORLDBANK
rest_time = 0#s time the computer can rest after [save_thresh] IDs
# ____________________________________________________________________#

#________________________ Print/plot settings ________________________#
viewData = False # Indicates whether you just want to view the initial data
do_print = False # Indicate whether output should be printed (useful for debugging)
plot = False # Plot the graph on html
if plot: editing = True # If we are editing, only draw the relevant piece (that corresponds to the ID) to the map
# ____________________________________________________________________#

#________________________ Mapbox accesstoken _________________________#
with open('./mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]
# ____________________________________________________________________#
"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""