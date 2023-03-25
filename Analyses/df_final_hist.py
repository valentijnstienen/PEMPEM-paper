import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import ast


# Load data (this data contains for each square all different shortest path lenghts).
# This data looks as follows
# _______________________________________________________________________________________________________________________________________________________________________________
#       Square                                          From                                            To  Trajectory_length        SP_OLD        SP_NEW  Percentage_difference
# 0        151  POINT (216056.5615611683 -43903.23267755478)  POINT (216983.0422276834 -43160.55450185434)        1977.098163   2033.728055   2033.728055           1.118014e-14
# 1        106    POINT (206837.59514312 -65008.87109097657)   POINT (209472.154814576 -63173.12784336951)        3917.258195   4033.784651   4033.784651           1.127347e-14
# 2        186  POINT (227683.3628359265 -82887.43230308793)  POINT (226315.3624812515 -84151.62511232925)        4209.309868   4032.799526   4032.799526           1.127622e-14
# _______________________________________________________________________________________________________________________________________________________________________________
df = pd.read_table("df_final_FULL_2.csv", sep = ";", index_col = 0) # _2_NEW

# Find distances between the projected points
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
distances_between_from = pairwise_distance_between_cols(df.From_P_OLD, df.From_P_NEW)
distances_between_to = pairwise_distance_between_cols(df.To_P_OLD, df.To_P_NEW)
# # Look at the shortest paths that have thier points projected at the same spot. We can only compare the lenghts of these shortest paths...
SAME_PROJECTION = 5 #m
same_projection_ids = list(np.where((np.array(distances_between_from) <= SAME_PROJECTION) & (np.array(distances_between_to) <= SAME_PROJECTION))[0])
df = df.loc[same_projection_ids, :].reset_index(drop = True)

# ignore cases where SP legnth was 0 or when SP was not available
# MIN_SP_DIFFERENCE = 10 #%
# df =df[(df.SP_OLD > MIN_SP_DIFFERENCE) & (df.SP_NEW > MIN_SP_DIFFERENCE)].reset_index(drop=True)

# df['diff_old_trajectory'] = (np.abs(df.Trajectory_length - df.SP_OLD)/df.Trajectory_length)*100
# MAX_PERCENTAGE_DIFFERENCE_SP_TR = 5 #%
# df = df[df.diff_old_trajectory < MAX_PERCENTAGE_DIFFERENCE_SP_TR].reset_index(drop=True)

# Extract specific square information
def print_info(square):
    percentage_diffs = df.loc[df.Square == square, 'Percentage_difference'] # or np.mean(df.loc[df.Square == square, 'Percentage_difference'])
    print("Square", square, ": Mean percentage difference:", np.mean(percentage_diffs), "(" + str(len(percentage_diffs)) +" OD pairs)")
    print("Square", square, ": Median percentage difference:", np.median(percentage_diffs), "(" + str(len(percentage_diffs)) +" OD pairs)")
for s in [57, 176]: print_info(s)

# Group the data per square (for creating the histogram)
df_grouped_square = df.groupby(['Square']).agg({'Percentage_difference': 'mean'}).reset_index(drop=False)
df_grouped_square.sort_values(by = ['Percentage_difference'], inplace = True)
print(list(df_grouped_square))
percentage_differences = df_grouped_square.Percentage_difference #df.Percentage_difference if you want to consider each OD pair comparison separately
print("Mean percentage difference:", np.mean(percentage_differences))
print("Median percentage difference:", np.median(percentage_differences))

# Define figure
plt.figure()
plt.title("Percentage decreases")

MIN_PERCENTAGE_DECREASE = 0 #1%
MAX_PERCENTAGE_DECREASE = max(percentage_differences)

# Different kind of plots
#a, b, c = plt.hist(percentage_differences, bins=100, range=[MIN_PERCENTAGE_DECREASE,MAX_PERCENTAGE_DECREASE], density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)
a, b, c = plt.hist(np.clip(percentage_differences, MIN_PERCENTAGE_DECREASE, MAX_PERCENTAGE_DECREASE), bins=120, range=[MIN_PERCENTAGE_DECREASE,MAX_PERCENTAGE_DECREASE], density=False, weights=None, cumulative=False, bottom=None, histtype='bar', align='mid', orientation='vertical', rwidth=None, log=False, color=None, label=None, stacked=False, data=None)
#plt.boxplot(percentage_differences)

# If we want to recreate the plot in latex, save the values to a csv
pd.DataFrame(a).to_csv("perf_percentage_differences_FINAL.csv")

# Show plot
plt.show()

