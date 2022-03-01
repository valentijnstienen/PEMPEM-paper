# Analyses 
In this folder, we can examine the performance of the created networks. We do this by comparing shortest paths in the initial and extended network. Note that this procedure can only be executed when an extended network exists. 

For the start and end points of the shortest paths we use the start and end points of the subtrips created using the pre-processing algorithm. Now, we start with creating a dataset that includes for all the Origin/Destination (OD) pairs. The shortest path length in the initial and in the extended network. 

From | To | SP_OLD | SP_NEW | Diff | From_projected | Minimal_projection_distance_from | From_projected_distance | To_projected | Minimal_projection_distance_to | To_projected_distance | From_projected_NEW | Minimal_projection_distance_from_NEW | From_projected_distance_NEW | To_projected_NEW |	Minimal_projection_distance_to_NEW | To_projected_distance_NEW | Distance_between_from | Distance_between_to
 --- |--- |--- | --- |--- |--- |--- |--- |--- |--- |--- |---| ---| --- |--- |--- |--- |---|---
POINT(205731.6927375596 -39024.65810011271)	| POINT(204650.2855455943 -39772.95674411015)	| 1659.7	| 1659.7 | 0.0	| (205734.13828451364, -39024.15897507633)	| 2.5	| 2.5	| (204646.862610691, -39775.039426025236) |	4.0 |	4.0	| (205734.13828451364, -39024.15897507633)	| 2.5	| 2.5	| (204646.862610691, -39775.039426025236) |	4.0 |	4.0 |	0.0 |	0.0 
POINT(204665.8870010334 -39795.08210889951) |	POINT(205727.2364201575 -39022.44639382615)	| 1630.7	| 1627.7	| 3.1	| (204660.90277633906, -39798.11475629857)	| 5.8	| 5.8	| (205733.5267317863, -39021.16256976572) |	6.4	| 6.4	| (204660.90277633906, -39798.11475629857)	| 5.8	| 5.8	| (205734.13828451364, -39024.15897507633) | 6.4	| 6.4	| 0.0	| 3.0581761760522777

We start with creating a the 

As for the main algorithm, start with specifying the settings for the analyses (use [SETTINGS_ANALYSES.py](https://github.com/valentijnstienen/PEMPEM-paper/blob/main/Analyses/SETTINGS_ANALYSES.py)). 



```
$ python RoutingResults.py
```


```
$ python ResultsSP.py
```
