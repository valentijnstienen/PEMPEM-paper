# Data pre-processing
There are two pre-processing situations. We want to pre-process a given set of 
1. GPS trajectories obtained from a GPS tracker ([GPS trajectory pre-processing](#GPStraj)).
2. roads, represented as GPS trajectories, based on their geometry ([Road geometry pre-processing](#Merging)).

<a name="GPStraj"></a>
## GPS trajectory pre-processing
Here, we pre-process any raw output from GPS trajectories to the desired format used in the algorithm (see Section 3 in the paper). Any raw data used looks as follows:

| Date                |Latitude|Longitude|Speed  |Course |
| :------------------ |-------:|--------:|------:|------:|
| 2020-04-11 11:46:44 |-0.74603|100.53225 | 23.9 | 132  | 
| 2020-04-11 11:46:51 |-0.75559|100.54749 | 25.0 | 133 |
| 2020-04-11 11:47:51 |-0.75339|100.55469 | 37.4 | 126 |
| ... | ... | ... | ... | ... |

For the desired format, we want to extract subtrips from this initial raw data; trips for which we assume that they consist of GPS points that were received "in one go", without any outlying points. Moreover, we want to obtain information about the Most Likely Distance Covered (MLDC), and the Maximum Distance Covered (MDC). For more details, we refer to the paper. These numbers will be based on:

* MLDC: the minimal distance that can be covered using geographical locations.
* MLDC: the maximal distance that can be covered using the velocity and time staps. 
* MDC: the maximal distance that can be covered using the change in time stamps.

This pre-processing algorithm subdivides the raw data into subtrips (with different IDs) and computes, among other things that might be interested, the quantities described above. The end result will contain at least this information and will look as follows:

| Date                |Latitude|Longitude|Course |MinDistance_LOC | MaxDistance_VELTIME | MaxDistance_TIME | ID |
| :------------------ |-------:|--------:|------:|----:|----:|----:|----:|
|2019-10-27 19:36:48|-0.3527|102.3564|-1|99999|99999|99999|1
|2019-10-27 19:37:18|-0.3542|102.3567|175|171.6|197.5|666.7|1
|2019-10-27 19:37:48|-0.3554|102.3562|231|146.2|197.5|666.7|1
|2019-10-27 19:37:48|-0.3554|102.3562|229|133.2|162.4|644.4|1
| ... | ... | ... | ... | ... | ... |


<a name="Merging"></a>
## Road geometry pre-processing
Here, we pre-process any raw roads represented as GPS trajectories to the desired format used in the algorithm (see Section 3 in the paper). Such data looks like:

| Latitude|Longitude| ID  |
| ------:|--------:|------:|
| -8.55919|125.57995 | A01 | 
| -8.55870|125.58102 | A01 |
| -8.55852|125.58140 | A01 |
| ... | ... | ... | 

where the ID refers to a specific road in the dataset that is transformed into a set of GPS trajectories. Note that in this case, we are quite certain about the locations in these trajectories. We now only add the course, and determine the covered distances exactly based on the locations of the points in this dataset.  

## Running the pre-processing algorithm
The pre-processing algorithm is built-in the original application. In other words, you do not need to run this pre-processing algorithm explicitly. However, you can, by executing the following code in your command line: 

```
$ python CreateTraces_Preprocessing.py
```
