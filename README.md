# PEMPEM-paper
Supplements to the paper "Enrich digital road networks for optimization in remote areas using GPS trajectories".

[comment]: <> (Include authors)

In this paper we discuss how to extend a given initial graph with the information in GPS trajectories. An initial graph can either be 


The GPS trajectories that are used to extend your initial graph should be saved in a CASE folder within the existing Data folder. An example of such raw GPS trajectory data is shown below:

| Date                |Latitude|Longitude|Speed  |Course |
| :------------------ |-------:|--------:|------:|------:|
| 2020-04-11 11:46:44 |-0.74603|100.53225 | 23.9 | 132  | 
| 2020-04-11 11:46:51 |-0.75559|100.54749 | 25.0 | 133 |
| 2020-04-11 11:47:51 |-0.75339|100.55469 | 37.4 | 126 |
| ... | ... | ... | ... | ... |

## Data pre-processing
If your raw data needs pre-processing (most likely), make sure you verify (adjust when necessary) the settings for the pre-processing algorithm ([Settings_PreprocessingAlgorithm.py](https://github.com/valentijnstienen/PEMPEM-paper/blob/main/Data%20(github)/SETTINGS_PreprocessingAlgorithm.py)) according to your wishes. For more details on the data pre-processing, we refer to the corresponding [Data pre-processing page](https://github.com/valentijnstienen/PEMPEM-paper/tree/main/Data%20(github)).


## Running the algorithm
Before running the algorithm, you need to define the settings of the algorithm ([SETTINGS.py](https://github.com/valentijnstienen/PEMPEM-paper/tree/main/SETTINGS.py)). After filling in these settings, you can run the algorithm by executing the following commands:

```
$ python mainRun.py
```


