# Data pre-processing
Here, we pre-process (if needed) any raw output from GPS trajectories to the desired format <br /> used in the algorithm (see Section 3 in the paper). Any raw data used looks as follows:

| Date                |Latitude|Longitude|Course |
| :------------------ |-------:|--------:|------:|
| 2020-04-11 11:46:44 |-0.74603|100.53225 | 132   | 
| 2020-04-11 11:46:51 |-0.75559|100.54749 | 133   |
| 2020-04-11 11:47:51 |-0.75339|100.55469 | 126   |
| ... | ... | ... | ... |

For the desired format, we want to extract subtrips from this initial raw data; trips for which <br /> we assume that they consist of GPS points that were received "in one go", without any outlying <br /> points. Moreover, we want to obtain information about the Most Likely Distance Covered <br />(MLDC), and the Maximum Distance Covered (MDC). For more details, we refer to the paper. <br /> These numbers will be based on:

* MLDC: the minimal distance that can be covered using geographical locations.
* MLDC: the maximal distance that can be covered using the velocity and time staps. 
* MDC: the maximal distance that can be covered using the change in time stamps.

This pre-processing algorithm subdivides the raw data into subtrips (with different IDs) and <br />computes, among other things that might be interested, the quantities described above. The<br /> end result will contain at least this information and will look as follows:

| Date                |Latitude|Longitude|Course |MinDistance_LOC | MaxDistance_VELTIME | MaxDistance_TIME | ID |
| :------------------ |-------:|--------:|------:|----:|----:|----:|----:|
|2019-10-27 19:36:48|-0.3527|102.3564|-1|99999|99999|99999|1
|2019-10-27 19:37:18|-0.3542|102.3567|175|171.6|197.5|666.7|1
|2019-10-27 19:37:48|-0.3554|102.3562|231|146.2|197.5|666.7|1
|2019-10-27 19:37:48|-0.3554|102.3562|229|133.2|162.4|644.4|1
| ... | ... | ... | ... | ... | ... |
