# TBA Time Predictions

Here live some scripts and graphs for analyzing time predictions on The Blue Alliance.

## Setup

You should probably use a python Virtual Environment for this. Install the dependencies with:

```
pip install -r requirements.txt
```

## TBA Dependencies

These scripts assume you have a functioning local install of [The Blue Alliance](https://github.com/the-blue-alliance) that has match data for 2017. The location of the TBA codebase should be at `../the-blue-alliance` (relative to this directory). In addition, it uses the Google App Engine [remote API](https://cloud.google.com/appengine/docs/standard/python/tools/remoteapi) to interact with the database.

## Build Cycle Distribution

Run the script `build_cycle_distribution.py` and `dist_fit.py` to generate cycle time data and draw a histogram.

![](https://github.com/phil-lopreiato/tba-time-predictions/blob/master/2017cycles_trend.png?raw=true)

## Calculate Event Stats

To generate schedule graphs for a given event, run the `error_calc.py` script and pass it the port of the remote API for the local dev instance. You can run this for multiple events. Afterwards, run `draw_errors.py` to generate on-timeness graphs.

```
./error_calc.py --url localhost:37849 --event 2017nyny
./draw_errors.py
```

![](https://github.com/phil-lopreiato/tba-time-predictions/blob/master/2017nyny_error.png?raw=true)

![](https://github.com/phil-lopreiato/tba-time-predictions/blob/master/2017nyny_sched_error.png?raw=true)
