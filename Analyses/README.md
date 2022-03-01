# Analyses 
In this folder, we can examine the performance of the created networks. We do this by comparing shortest paths in the initial and extended network. Note that this procedure can only be executed when an extended network exists. 

For the start and end points of the shortest paths we use the start and end points of the subtrips created using the pre-processing algorithm. Now, we start with creating a dataset that includes for all the Origin/Destination (OD) pairs. The shortest path length in the initial and in the extended network. 

From | To | SP_OLD | SP_NEW | Diff | From_projected | Minimal_projection_distance_from | From_projected_distance | To_projected | Minimal_projection_distance_to | To_projected_distance | From_projected_NEW | Minimal_projection_distance_from_NEW | From_projected_distance_NEW | To_projected_NEW	Minimal_projection_distance_to_NEW | To_projected_distance_NEW | Distance_between_from | Distance_between_to
 --- |--- |--- | --- |--- |--- |--- |--- |--- |--- |--- |---| ---| --- |--- |--- |--- |---

We start with creating a the 

As for the main algorithm, start with specifying the settings for the analyses (use [SETTINGS_ANALYSES.py](https://github.com/valentijnstienen/PEMPEM-paper/blob/main/Analyses/SETTINGS_ANALYSES.py)). 



```
$ python RoutingResults.py
```


```
$ python ResultsSP.py
```
