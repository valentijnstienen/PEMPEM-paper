"""-------------------------------------------------------------------------"""
"""---------------------- PARAMETERS OF THE ALGORITHM ----------------------"""
"""-------------------------------------------------------------------------"""
SEED = 0
shuf = False
#____________________________ Define Case ____________________________#
CASE = "PEMPEM" #"WorldBank" #"PEMPEM" #TODO WORLDBANK # Folder name used for files that uses the specified data
CASENAME = "PEMPEM_FINAL" #"TimorLeste_EO"/"SMALL" #TODO WORLDBANK # (Sub)folder name used for files that include case-specific data (see below)
#_____________________________________________________________________#
preProcessTrajectories = True
PATH_TO_PRE_PROCESSED_TRAJECTORIES = "Data/PEMPEM/PEMPEM_subtrips_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv" #"Data/PEMPEM/PEMPEM_subtrips_125_3_80_10_5_5_ARTCOURSE_DIRECTION_False_1311.csv" #"Data/WorldBank/WorldBank_subtrips_0609_OSM.csv" "Data/WorldBank/WorldBank_subtrips_0609_estrada.csv" #TODO WORLDBANK
#_____________________________________________________________________#

#____________________________ Define Area ____________________________#
initializeGraph = True
if initializeGraph:
    """
    Use one of the following formats:
    - a region defined by a string (e.g., "timor leste") 
    - a rectangle defined by a list with the form [lon_min, lon_max, lat_min, lat_max] (e.g., [101.85, 102.99, -1.04, -0.18])
    - a polygon defined by a list of points. (e.g.,: [(101.91454,-0.46966), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)])
    - a shapefile that can be transformed into a graph defined by its path. Include the whole area that may be extended

    PATH_TO_SHAPEFILE_INITIAL = 'Data/WorldBank/_Shapefiles/roads.shp' # OSM as initial: 'Data/WorldBank/_Shapefiles/march22_osm_recent.shp' # eStrada as initial: 'Data/WorldBank/_Shapefiles/roads.shp'

    Use cases
    - PEMPEM (small): [(101.91454,-0.46966), (102.3965,-0.1993), (102.83846,-0.36753), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)]
    - WorldBank: "timor leste"
    """ 
    area = [(101.91454,-0.46966), (102.3965,-0.1993), (102.83846,-0.36753), (103.03708,-0.61819), (102.88269,-1.06313), (102.18326,-0.78009), (101.91454,-0.46966)] #[101.85, 102.99, -1.04,   -0.18] #TODO What if no idea of size polygon, use the information in the data_used.
    #area = ['Data/WorldBank/_Shapefiles/march22_osm_recent.shp','timor leste'] # OSM as initial: 'Data/WorldBank/_Shapefiles/march22_osm_recent.shp' # eStrada as initial: 'Data/WorldBank/_Shapefiles/roads.shp' # Second argument: area that we want to extend trajectories outside are ignored
#_____________________________________________________________________#

#__________________ Scope Settings for the algorithm _________________#
existing_ids = [0] # when starting: [0]
new_ids = range(1, 14961) #PEMPEM: range(1, 14961) # WB(OE): range(1,1101) # WB(EO): range(1,8001) 
# ____________________________________________________________________#

#______________ Mathematical Settings for the algorithm ______________#
max_dist_projection = [30, 50]# #\bar{d},\bar{\bar{d}} #TODO WORLDBANK     [30, 30] # [30, 50]           
max_bearingdiff_projection = [75, 75] #\bar{alpha},\bar{\bar{alpha}}    
max_dist_merge = 10 #meters
two_way = False #TODO WORLDBANK
merging_networks = False #TODO WORLDBANK
# ____________________________________________________________________#
# ____________________________________________________________________#


#________________________ DEVELOPER SETTINGS _________________________#
#_____________ Data limitation (only use in single new_id) ___________#
max_step_input = None # Maximum number of points examined within one ID, None: all
dat_range = None# range(531, 536) # Range that specifies the scope (points within a single ID) of the data (e.g., 245:345), None: all
#_____________________________________________________________________#

#___________________________ Save settings ___________________________#
load = True # True if you want to load the graph corresponding to the existing ids
save = True # True if you want to save the graphs/polygons during the run. (RECOMMENDED)
save_thresh = 500# Save the graph once every [save_thresh] IDs #TODO WORLDBANK
rest_time = 0#s time the computer can rest after [save_thresh] IDs
#_____________________________________________________________________#

#________________________ Print/plot settings ________________________#
viewData = False # Indicates whether you just want to view the initial data
do_print = False # Indicate whether output should be printed (useful for debugging)
plot = False # Plot the graph on html
if plot: editing = True # If we are editing, only draw the relevant piece (that corresponds to the ID) to the map
#_____________________________________________________________________#

#________________________ Mapbox accesstoken _________________________#
with open('./mapbox_accesstoken.txt') as f: mapbox_accesstoken = f.readlines()[0]
#_____________________________________________________________________#
"""-------------------------------------------------------------------------"""
"""-------------------------------------------------------------------------"""