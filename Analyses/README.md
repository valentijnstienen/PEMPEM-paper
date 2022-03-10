# Analyses 
In this folder, we can examine the performance of the created networks. We do this by comparing shortest paths in the initial and extended network. 

This analyses can be done for a given graph. For the start and end points of the shortest paths we use the start and end points of the subtrips created using the pre-processing algorithm. Now, we start with creating a dataset that includes, for all the Origin/Destination (OD) pairs, the shortest path length in the given graph network. Moreover, we want to include other metrics that might be interesting to see. The dataset that we create looks as follows:

From | To | SP | Minimal_projection_distance_from | From_projected | From_projected_distance | Minimal_projection_distance_to | To_projected | To_projected_distance | 
 --- |--- |--- | --- |--- |--- |--- |--- |--- 
POINT(205731.6927375596 -39024.65810011271)	| POINT(204650.2855455943 -39772.95674411015)	| 1659.7 | 2.5 | (205734.13828451364, -39024.15897507633)	| 2.5	| 4.0 | (204646.862610691, -39775.039426025236) |	4.0	
POINT(204665.8870010334 -39795.08210889951) |	POINT(205727.2364201575 -39022.44639382615)	| 1630.7	| 5.8 | (204660.90277633906, -39798.11475629857)	| 5.8	| 6.4 | (205733.5267317863, -39021.16256976572) |	6.4

where: 
- `From` and `To` represent the origin and destination point (note that these are projected).
- `SP` is the length of the shortest path between the origin and destination in the given network. 
- `From_projected` (`To_projected`) represents the projection point of the origin (destination) in the graph. 
- `From_projected_distance` (`To_projected_distance`) are the final projection distances of the origin (destination) in the given graph.
- `Minimal_projection_distance_from`, `Minimal_projection_distance_to`. Note that we may not chose to project the origin (destination) on the closest edge. For instance, if a shorter path could be obtained with a different projection (while still satisfying the maximum projection distance threshold). Therefore, we also include the minimum possible distance to an edge. This is used to determine whether it is possible to project on an edge. 

Now, to create such a dataset, start with specifying the settings for the analyses (use [SETTINGS_Analyses.py](https://github.com/valentijnstienen/PEMPEM-paper/blob/main/Analyses/SETTINGS_Analyses.py)). Then, execute the following commands in your command line:

```
$ python RoutingResults.py
```





After having created this new dataset, we can use it to determine some performance indicators of the new network. Also here, we can choose between different indicators. 

- **Percentage of shortest paths (SPs) that can be found**: Here, we differentiate between reasons why a shortest could not be found (e.g., due to an unprojectable origin (destination)). 
- **Plot the points that could not be projected**: This gives insight in the regions where most origins/destination could (not) be projected on the network. An example of such a plot is given below:

<img src="readmefigures/projectable_points_plot.png" width="600">

- **Average projection distances**: Compare for both the graphs (initial/extended) the distance from the origin/destination points to their respective projections.

- **Frequency plots of actual/percentage decreases in SP length**: These plots can be used to get information about the distribution of the magnitude of the differences in shortest path length between the initial and the extended graph.

The settings are stored in the file itself: [ResultsSP.py](https://github.com/valentijnstienen/PEMPEM-paper/blob/main/Analyses/ResultsSP.py). This means that you need to open this file and specify your wishes here. Then, execute the following commands in your command line:

```
$ python ResultsSP.py
```
