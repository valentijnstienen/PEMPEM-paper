# Date       : 11-01-2021
# Environment: conda activate ox
# Location   : cd "Documents/Uvt/PhD/PEMPEM paper/Code/Create Network (BASE)/Data"
# Run        : python LoadDataOSM.py

import pandas as pd
import numpy as np 
from math import radians, cos, sin, asin, sqrt, atan2, pi
import datetime
import os, sys

if __file__ == 'mainRun.py': PATH_TO_PRESETTINGS = "Data/"
else: PATH_TO_PRESETTINGS = "./"

# Load settings
exec(open(PATH_TO_PRESETTINGS + "SETTINGS_PreprocessingAlgorithm.py").read())


def createSubtrips(filename, file_ID, merging, fname = None):
    """
    This function creates the DataFrame that we will work with. 

    Parameters
    ----------
    filename : string
        file name, e.g. PEMPEM_data when loading full dataset
    file_ID : list (consisting of numbers)
        list with the IDs to be incorporated. One ID corresponds to one vehicle on one day
   
    Returns
    -------
    subtrips : pandas DataFrame 
        
        A sample of this dataframe
                       DateTime  Latitude  Longitude  Speed  Course MinDistance_LOC MinDistance_VELTIME MaxDistance_VELTIME MaxDistance_TIME  ID
        0   2019-10-27 19:36:48  -0.35269  102.35638  17.40     159           99999               99999               99999            99999   1
        1   2019-10-27 19:37:18  -0.35420  102.35670  23.70     175         171.633             171.633               197.5          666.667   1
        2   2019-10-27 19:37:48  -0.35542  102.35621  16.33     231          146.19              146.19               197.5          666.667   1
        3   2019-10-27 19:38:17  -0.35632  102.35542  20.16     229         133.159             133.159               162.4          644.444   1
        4   2019-10-27 19:38:47  -0.35718  102.35403  21.87     252         181.749             181.749              182.25          666.667   1
    """
    if merging: 
        # Load complete dataset
        df_full = pd.read_table(filename, sep = ",", usecols=['Latitude', 'Longitude', 'ID'])
        df_full = df_full[df_full.ID != '0'] # remove (switching) rows that indicate where a new road starts

        # Use numerical IDs instead of random strings
        i = df_full.ID
        df_full.ID = i.ne(i.shift()).cumsum()  
        df_full = df_full[df_full["ID"].isin(file_ID)]
    
        # Preprocess data
        df_full.Latitude = pd.to_numeric(df_full['Latitude'])#.round(decimals=4)
        df_full.Longitude = pd.to_numeric(df_full['Longitude'])#.round(decimals=4)
        df = df_full.reset_index(drop=True)
    
        # Unique IDs in the full dataset
        uniqueIDs = df.ID.unique()
    
        # Initialize subtrip dataset
        subtrips = pd.DataFrame(columns=df.columns)
    
        for i in file_ID:
            print("Working on ID: " + str(i))
        
            # If the current ID does not exist, skip this id and continue with the next. 
            if (i not in uniqueIDs): continue
        
            # Create temporary dataset that only contains data from the current ID
            df_temp = df[df.ID==i].copy().reset_index(drop=True)
        
            # Create the trips (add start and end point per trip). This new dataset is called df_new
            #cols = ['Latitude', 'Longitude', 'Course', 'subID', "MinDistance_LOC", "MinDistance_VELTIME", "MaxDistance_VELTIME", "MaxDistance_TIME",'ID']
        
            # Add course to the dataset
            df_temp['Course'] = -1
            for s in range(0, len(df_temp)-1):
                start_point = (df_temp.loc[s, 'Latitude'], df_temp.loc[s,'Longitude'])
                end_point = (df_temp.loc[s+1, 'Latitude'], df_temp.loc[s+1,'Longitude'])
                df_temp.loc[s, 'Course'] = computeBearing(start_point, end_point)
        
            # Add distance covered
            df_temp['MinDistance_LOC'] = 99999
            df_temp['MinDistance_VELTIME'] = 99999
            df_temp['MaxDistance_VELTIME'] = 99999
            df_temp['MaxDistance_TIME'] = 99999
            for s in range(1, len(df_temp)):
                dist = haversine(df_temp.loc[s, 'Latitude'], df_temp.loc[s,'Longitude'], df_temp.loc[s-1, 'Latitude'], df_temp.loc[s-1,'Longitude'])
                df_temp.loc[s, 'MinDistance_LOC'] = dist
                df_temp.loc[s, 'MinDistance_VELTIME'] = dist
                df_temp.loc[s, 'MaxDistance_VELTIME'] = dist
                df_temp.loc[s, 'MaxDistance_TIME'] = dist#+10

            # Add the subtrips to the final dataframe
            subtrips = subtrips.append(df_temp).reset_index(drop=True)
        
        # Change data structures of subtrips
        subtrips = subtrips.astype({"ID": int, "Course": int})
    
        # Round some of the numbers
        subtrips.loc[:, ["Latitude", "Longitude", 'MinDistance_LOC', 'MinDistance_VELTIME', 'MaxDistance_VELTIME', 'MaxDistance_TIME']] = subtrips.round({'Latitude': 6, 'Longitude': 6, 'MinDistance_LOC': 1, 'MinDistance_VELTIME': 1, 'MaxDistance_VELTIME': 1, 'MaxDistance_TIME': 1})
    
        # Count subids and remove some of them if too small (Based on subtrip_threshold)
        counttab = subtrips.ID.value_counts()
        subIDs_rem = list(counttab.index[counttab > 1])
        subtrips = subtrips[subtrips["ID"].isin(subIDs_rem)].reset_index(drop = True)
    
        # Rearrange columns a little bit
        cols = ['Latitude', 'Longitude', 'Course', 'MinDistance_LOC', 'MinDistance_VELTIME', 'MaxDistance_VELTIME', 'MaxDistance_TIME', 'ID']
        subtrips = subtrips[cols].reset_index(drop = True)
    
        # Save the dataset
        subtrips.to_csv(PATH_TO_PRESETTINGS + fname, sep = ";")    
    else:
        # Load the settings of the pre-processing algorithm
        #exec(open("./SETTINGS_PreprocessingAlgorithm.py").read())

        # Load and pre-process complete dataset
        df_full = pd.read_table(filename, sep = ";", usecols=['DateTime', 'Latitude', 'Longitude','Speed','Course', 'ID'])
        df_full = df_full[df_full["ID"].isin(file_ID)]
        df_full.Latitude = pd.to_numeric(df_full['Latitude'])
        df_full.Longitude = pd.to_numeric(df_full['Longitude'])
        df = df_full.reset_index(drop=True)
        df['DateTime'] = pd.to_datetime(df['DateTime'])

        # Initialize subtrip dataset (ouput)
        subtrips = pd.DataFrame(columns=df.columns.union(["subID"], sort = False))
        df_fromto = pd.DataFrame(columns = ['Latitude_from', 'Longitude_from', 'Latitude_to', 'Longitude_to', 'ID']) 
    
        for i in file_ID :
            print("Working on ID: " + str(i))
        
            # If the current ID does not exist, skip this id and continue with the next. 
            if (i not in df.ID.unique()): continue
        
            # Create temporary dataset that only contains data from the current ID
            df_temp = df[df.ID==i].copy().reset_index(drop=True)
        
            # Next we want to extract the up and down streaks of df_temp
            # Up = True: vehicle is moving, or stops for a short amount of time (traffic light) [MAX_DOWN_TIME]. Still driving the same trip. 
            # Up = False: vehicle is (un)loading, not driving the network. These are start/end points of trips
        
            # First, classify all points at which the vehicle was driving as "Up"
            df_temp["Up"] = df_temp.Speed >= DOWN_SPEED
        
            # If a vehicle was starting in an "Up" state (which is strange...), add a starting row in the down state
            if df_temp.Up[0]:
                tempRow = df_temp.iloc[0,:].copy()
                tempRow.Up = False
                tempRow.DateTime = tempRow.DateTime - datetime.timedelta(seconds = 30)
                df_temp.loc[-1] = tempRow # adding a row
                df_temp.index = df_temp.index + 1  # shifting index
                df_temp = df_temp.sort_index()  # sorting by index
        
            # 1. Start with defining all streaks based on the "Up" and "Down" states
            sos = df_temp.Up.ne(df_temp['Up'].shift())
            df_temp['streak_id'] = sos.cumsum()
        
            # 2. Determine streak ids that should be considered as up (just waiting below MAX_DOWN_TIME minutes, e.g., traffic light)
            df_temp["timediff"] = (df_temp['DateTime'] - df_temp['DateTime'].shift()).dt.total_seconds() # time difference between GPS points
            temp_df = df_temp.groupby(['streak_id', 'Up']).agg({'timediff': 'sum'}).reset_index()
            l = list(temp_df[(temp_df.Up == False) & (temp_df.timediff <= MAX_DOWN_TIME)].streak_id)
            # Update the df_temp (in particular the Up column)
            idx = df_temp[df_temp.streak_id.isin(l)].index
            idx = [v for v in idx if v != 0]
            df_temp.loc[idx, "Up"] = True
            # update the streak ids (now including the new parts)
            sos = df_temp.Up.ne(df_temp['Up'].shift())
            df_temp['streak_id'] = sos.cumsum()
        
            # 3. For each down time > MAX_DOWN_TIME, start a new trip (there is too much time inbetween GPS points for it to be reliable)
            for md in np.where(df_temp.timediff > MAX_DOWN_TIME)[0]: 
                df_temp.loc[md:, 'streak_id'] = df_temp.streak_id[md:] + 1
        
            # Extract start and end point of the ID 
            startend_points = df_temp.groupby(['streak_id', 'Up']).agg({'Latitude' : np.mean, 'Longitude' : np.mean, 'Speed': np.mean, 'Course': np.mean, 'ID': 'first', 'DateTime': ['first', 'last']}).reset_index()
            startend_points.columns = ['streak_id', 'Up', 'Latitude', 'Longitude', 'Speed', 'Course', 'ID', 'DateTime_start', "DateTime_end"]
            startend_points_true = startend_points[startend_points.Up == True].reset_index(drop = True)

            # Create the trips (add start and end point per trip). This new dataset is called df_new
            cols = ['DateTime', 'Latitude', 'Longitude', 'Speed', 'Course', 'subID', "MinDistance_LOC", "MinDistance_VELTIME", "MaxDistance_VELTIME", "MaxDistance_TIME",'ID']
            df_new = pd.DataFrame(columns = cols) #
            subid = 0  # Define first subID number

            for s in startend_points_true.streak_id:

                # 1. Start with extracting relevant data
                driving_piece = df_temp[df_temp.streak_id == s][cols[0:5]+['timediff'] + ['ID']].reset_index(drop=True) #s in the paper
            
                # 2. Create a new dataframe) (without outliers)
                driving_piece_without_outliers = pd.DataFrame(columns = cols) #T' in the paper
                len_dp = range(0,len(driving_piece))
                t = 0

                # Note that we use a while loop as the driving piece may change (we could cut it and therefore we also set len_dp beforehand)
                while t in len_dp:
                    # First point, speed and time is ignored, as there is no reliable time stamp of previous point
                    if (len(driving_piece_without_outliers) == 0): 
                        # When we are not sure about the course, we have one option 
                        # (1) Base the course on the direction of the edge (can also always be done)
                        if (driving_piece.loc[t, "Course"] == 0) | ALWAYS_COURSE:
                            if len(driving_piece) > 1:
                                start_point = (driving_piece.loc[t, "Latitude"], driving_piece.loc[t, "Longitude"])  
                                end_point = (driving_piece.loc[t+1, "Latitude"], driving_piece.loc[t+1, "Longitude"]) 
                                driving_piece.loc[t, "Course"] = computeBearing(start_point, end_point)
                        else: driving_piece.loc[t, "Course"] = -1 
                        # Add point to T'
                        driving_piece_without_outliers.loc[len(driving_piece_without_outliers)] = [driving_piece.loc[t,'DateTime'], driving_piece.loc[t,'Latitude'], driving_piece.loc[t,'Longitude'], driving_piece.loc[t,'Speed'], driving_piece.loc[t,'Course'], subid, 99999, 99999, 99999, 99999, i]
                        t += 1
                        continue
                    else:
                        # Determine ACF distance = Linear Distance Covered. 
                        ACF_distance_covered = haversine(driving_piece.loc[t,'Latitude'], driving_piece.loc[t,'Longitude'], driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, 'Latitude'], driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, 'Longitude'])
                    
                        # If the point is too close to the previous point, we do not add it to T'. We immediately start examining the next point.
                        if (ACF_distance_covered < MIN_ACF_DISTANCE_COVERED): 
                            t += 1
                            continue
                    
                        # Determine max distance that could be covered when driving MAX_SPEED for the full amount of seconds
                        max_distance_speed_time = (driving_piece.loc[t,'DateTime'] - driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'DateTime']).total_seconds() * MAX_SPEED * (1000/3600)
                    
                        # When we are not sure about the speed, we have one option 
                        # (1) Base the speed on the previous and next (real) speed
                        if (driving_piece.loc[t, "Speed"] == 0):
                            # Find the speed of the first reliable point
                            next_speed, tt = 0, t
                            while (next_speed == 0) & (tt < (len(driving_piece)-1)):
                                next_speed = driving_piece.loc[tt+1, "Speed"]
                                tt += 1
                            if (tt == (len(driving_piece)-1)) & (next_speed == 0): # Could only happen when streak was split by MAX_DOWN_TIME
                                driving_piece.loc[t:(tt-1), "Speed"] = driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, "Speed"] #Set equal to the last known speed.
                            else: driving_piece.loc[t:(tt-1), "Speed"] = (driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, "Speed"] + driving_piece.loc[tt, "Speed"])/2
                    
                        # If we can at least reach the point when driving full speed, we include the GPS point in the df_new
                        SITUATION_1 = (ACF_distance_covered < max_distance_speed_time)
                        SITUATION_2 = (driving_piece.loc[t,'DateTime'] - driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'DateTime']).total_seconds() > MIN_TIME_BETWEEN_POINTS

                        # Add the point to the temporary trip T'
                        if  SITUATION_1 & SITUATION_2: # Distance could be covered in time and minimal time satisfied
                            # Determine minimum/maximum speed to reach this point (based on speed)
                            actual_speed_min = min(driving_piece.loc[t,'Speed'], driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'Speed'])
                            actual_speed_max = max(driving_piece.loc[t,'Speed'], driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'Speed'])
                    
                            # Determine minimum/maximum distance covered to reach this point (based on time and actual speed (min/max)
                            actual_distance_speed_time_min = (driving_piece.loc[t,'DateTime'] - driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'DateTime']).total_seconds() * actual_speed_min *(1000/3600)
                            actual_distance_speed_time_max = (driving_piece.loc[t,'DateTime'] - driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'DateTime']).total_seconds() * actual_speed_max *(1000/3600)
                    
                            # When using the acceleration idea
                            #initial_v = driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'Speed']*1000/3600 # m/s
                            #delta_t = (driving_piece.loc[t,'DateTime'] - driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1,'DateTime']).total_seconds() # s
                            #max_distance_acceleration = initial_v*delta_t + (1/2)*MAX_ACCELERATION*(delta_t**2)
                        
                            driving_piece.loc[t, "MinDistance_LOC"] = ACF_distance_covered
                            driving_piece.loc[t, "MinDistance_VELTIME"] = max(actual_distance_speed_time_min, ACF_distance_covered)
                            driving_piece.loc[t, "MaxDistance_VELTIME"] = max(actual_distance_speed_time_max, ACF_distance_covered)
                            driving_piece.loc[t, "MaxDistance_TIME"] = max_distance_speed_time
                        
                            # When we are not sure about the course, we have two options 
                            # (1) Base the course on the previous and next (real) course
                            # (2) Base the course on the direction of the edge (can also always be done)
                            option_course = 2
                            if (driving_piece.loc[t, "Course"] == 0) | ALWAYS_COURSE:
                                if option_course == 1: # OPTION (1)
                                    # Find the course of the first reliable point
                                    next_course, tt = 0, t
                                    while (next_course == 0) & (tt < (len(driving_piece)-1)):
                                        next_course = driving_piece.loc[tt+1, "Course"]
                                        tt += 1
                                    # There is no upcoming reliable point, set course equal to the course of the last point
                                    if (tt == (len(driving_piece)-1)) & (next_course == 0): driving_piece.loc[t:(tt-1), "Course"] = driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, "Course"]
                                    else: driving_piece.loc[t:(tt-1), "Course"] = meanCourse(driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, "Course"], driving_piece.loc[tt, "Course"])
                                elif option_course == 2: # OPTION (2)
                                    if t < len(driving_piece)-1:
                                        start_point = (driving_piece.loc[t, "Latitude"], driving_piece.loc[t, "Longitude"])  #(df_temp.loc[s, 'Latitude'], df_temp.loc[s,'Longitude'])
                                        end_point = (driving_piece.loc[t+1, "Latitude"], driving_piece.loc[t+1, "Longitude"]) #(df_temp.loc[s+1, 'Latitude'], df_temp.loc[s+1,'Longitude'])
                                        driving_piece.loc[t, "Course"] = computeBearing(start_point, end_point)
                                    else: driving_piece.loc[t, "Course"] = -1 # t == (len(driving_piece)-1) t is the last point

                            # Add point to the df
                            driving_piece_without_outliers.loc[len(driving_piece_without_outliers)] = driving_piece.loc[t].copy() 
                        elif (not SITUATION_1): # Finish the trip 
                            # Add the new cleaned driving piece to the new dataframe
                            driving_piece_without_outliers['subID'] = subid
                            df_new = df_new.append(driving_piece_without_outliers, ignore_index = True)
                        
                            fromto_point = list(driving_piece_without_outliers.loc[0, ['Latitude', 'Longitude']]) + list(driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, ['Latitude', 'Longitude']]) + [str(i) + "_" + str(subid)]
                            df_fromto.loc[len(df_fromto)] = fromto_point
                        
                        
                        
                            driving_piece_without_outliers = pd.DataFrame(columns = cols)
                        
                            # Start a new trip
                            driving_piece = driving_piece.loc[t::].reset_index(drop = True)
                            len_dp = range(0, len(driving_piece))
                            t = 0
                        
                            subid += 1
                            continue    
                        t += 1
                    
                # Add the new cleaned driving piece to the new dataframe (this is the last part of the driving piece)
                driving_piece_without_outliers['subID'] = subid
                df_new = df_new.append(driving_piece_without_outliers, ignore_index = True)
            
                # Fill the routing dataframe
                fromto_point = list(driving_piece_without_outliers.loc[0, ['Latitude', 'Longitude']]) + list(driving_piece_without_outliers.loc[len(driving_piece_without_outliers)-1, ['Latitude', 'Longitude']]) + [str(i) + "_" + str(subid)]
                df_fromto.loc[len(df_fromto)] = fromto_point

                subid += 1

            # Add the subtrips to the final dataframe
            subtrips = subtrips.append(df_new).reset_index(drop=True)
        
        # Change data structures of subtrips
        subtrips = subtrips.astype({"ID": int, "Course": int})

        # Finalize subtrips dataset 
        subtrips["tripID"] = [str(i) + "_" + str(j) for i, j in zip(subtrips.ID, subtrips.subID)]
    
        # Round some of the numbers
        subtrips.loc[:, ["Latitude", "Longitude", 'MinDistance_LOC', 'MinDistance_VELTIME', 'MaxDistance_VELTIME', 'MaxDistance_TIME']] = subtrips.round({'Latitude': 6, 'Longitude': 6, 'MinDistance_LOC': 1, 'MinDistance_VELTIME': 1, 'MaxDistance_VELTIME': 1, 'MaxDistance_TIME': 1})

        # Count subids and remove some of them if too small (Based on subtrip_threshold)
        counttab = subtrips.tripID.value_counts()
    
        subIDs_rem = list(counttab.index[counttab >= MIN_SUBTRIP_LENGTH])
        subtrips = subtrips[subtrips["tripID"].isin(subIDs_rem)].reset_index(drop = True)
        #df_fromto = df_fromto[df_fromto["ID"].isin(subIDs_rem)].reset_index(drop = True)

        # Assign a unique number to each trip id in the final dataset. 
        i = subtrips.tripID
        subtrips['ID'] = i.ne(i.shift()).cumsum()
        df_fromto['ID'] = range(1,len(df_fromto)+1)
    
        # Drop irrelevant columns
        subtrips.drop(['subID', 'tripID'], axis='columns', inplace=True)
    
        # Rearrange columns a little bit
        cols = ['DateTime', 'Latitude', 'Longitude', 'Speed', 'Course', 'MinDistance_LOC', 'MinDistance_VELTIME', 'MaxDistance_VELTIME', 'MaxDistance_TIME', 'ID']
        subtrips = subtrips[cols].reset_index(drop = True)
    
        # Save the pre-processed dataset   
        if SAVE_STOPS: df_fromto.to_csv(PATH_TO_PRESETTINGS+FNAME_STOPS, sep = ";")
        subtrips.to_csv(PATH_TO_PRESETTINGS+fname, sep = ";")
    
"""---------------------------------------------------"""   
"""------------- SUPPLEMENTARY FUNCTIONS -------------"""   
"""---------------------------------------------------"""   
    
def meanCourse(alpha, beta): 
    """
    Compute the mean course/direction of two directions.
    """
    # Two possible mean courses (one in each direction)
    mean_1 = (alpha + beta)/2
    mean_2 = mean_1 + 180
    if (mean_2 > 360): mean_2 = mean_2 - 360
    # Check difference to the existing courses (both distance are the same)
    diff_1 = computeAngularDifference(alpha, mean_1)
    diff_2 = computeAngularDifference(alpha, mean_2)
    # Return the correct mean course
    if diff_1 < diff_2: return mean_1
    else: return mean_2

def computeBearing(start_point, end_point):
    """
    Calculate the compass bearing(s) between pairs of lat-lng points.
    Vectorized function to calculate (initial) bearings between two points'
    coordinates or between arrays of points' coordinates. Expects coordinates
    in decimal degrees. Bearing represents angle in degrees (clockwise)
    between north and the geodesic line from point 1 to point 2.
    Parameters
    ----------
    lat1 : float or numpy.array of float
        first point's latitude coordinate
    lng1 : float or numpy.array of float
        first point's longitude coordinate
    lat2 : float or numpy.array of float
        second point's latitude coordinate
    lng2 : float or numpy.array of float
        second point's longitude coordinate
    Returns
    -------
    bearing : float or numpy.array of float
        the bearing(s) in decimal degrees
    """
    lat1, lng1 = start_point[0], start_point[1]
    lat2, lng2 = end_point[0], end_point[1]
    
    # get the latitudes and the difference in longitudes, in radians
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)
    d_lng = np.radians(lng2 - lng1)

    # calculate initial bearing from -180 degrees to +180 degrees
    y = np.sin(d_lng) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(d_lng)
    initial_bearing = np.degrees(np.arctan2(y, x))

    # normalize to 0-360 degrees to get compass bearing
    return initial_bearing % 360
    
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r * 1000

def computeAngularDifference(alpha, beta):
    """
     Returns the angular difference between the angles/courses alpha and beta (in degrees)
    """
    check = abs(float(alpha)-float(beta))
    if check > 180: check = abs(check - 360)
    return check

"""---------------------------------------------------"""   
"""---------------------------------------------------"""   
createSubtrips(PATH_TO_PRESETTINGS+PATH_TO_RAW_GPSTRAJECTORIES, FILE_IDS_USED, merging = MERGING, fname = FNAME) 
