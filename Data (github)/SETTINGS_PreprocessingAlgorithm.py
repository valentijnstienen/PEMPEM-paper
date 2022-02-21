"""-----------------------------------------"""
""" Settings of the preprocessing algorithm """
"""-----------------------------------------"""

# PATH to the csv file with the (raw) GPS trajectories
PATH_TO_RAW_GPSTRAJECTORIES = 'WorldBank/coordinates_OSM_FULL_0609.csv' #PEMPEM: PEMPEM_data, #WB (eStrada as base, OSM as trajectories): coordinates_OSM_FULL_0609 #WB (OSM as base, eStrada as trajectories): coordinates_ESTRADA_FULL_0609 

FILE_IDS_USED = range(0,5)  #PEMPEM: range(0,2656), #WB (eStrada as base, OSM as trajectories): range(0,8001) #WB (OSM as base, eStrada as trajectories): range(0,1101)
MERGING = True

if MERGING: 
    #######################################
    ######### NEEDED WHEN MERGING #########
    #######################################
    FNAME = 'WorldBank/WorldBank_subtrips_0609_OSM.csv' #'WorldBank/WorldBank_subtrips_0609_estrada' #None: will create a name based on settings. 
    #######################################
else: 
    #######################################
    ######## NEEDED WHEN EXTENDING ########
    #######################################
    MAX_DOWN_TIME = 125 # seconds
    DOWN_SPEED = 3 # km/h
    MAX_SPEED = 80 # km/h
    MIN_ACF_DISTANCE_COVERED = 10 # meters
    MIN_TIME_BETWEEN_POINTS = 5 # seconds 
    MIN_SUBTRIP_LENGTH = 5
    ALWAYS_COURSE = False # True if we want to adjust the course always (not only when we are not sure)
    FNAME = 'PEMPEM/PEMPEM_subtrips_'+str(MAX_DOWN_TIME)+'_'+str(DOWN_SPEED)+'_'+str(MAX_SPEED)+'_'+str(MIN_ACF_DISTANCE_COVERED)+'_'+str(MIN_TIME_BETWEEN_POINTS)+'_'+str(MIN_SUBTRIP_LENGTH)+'_ARTCOURSE_DIRECTION_'+str(ALWAYS_COURSE)+'_1311.csv'
    # ------------------------------------#
    SAVE_STOPS = False
    FNAME_STOPS = 'PEMPEM/PEMPEM_stops_'+str(MAX_DOWN_TIME)+'_'+str(DOWN_SPEED)+'_'+str(MAX_SPEED)+'_'+str(MIN_ACF_DISTANCE_COVERED)+'_'+str(MIN_TIME_BETWEEN_POINTS)+'_'+str(MIN_SUBTRIP_LENGTH)+'_ARTCOURSE_DIRECTION_'+str(ALWAYS_COURSE)+'_1311.csv'
    #######################################
    
    # If using folders, make sure they exist before trying to open them! 
