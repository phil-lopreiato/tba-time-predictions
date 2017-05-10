#! /bin/env python

import argparse
import csv
import sys
import pytz
import os

start = os.getcwd()
os.chdir('../the-blue-alliance')
try:
    import dev_appserver
    dev_appserver.fix_sys_path()
    sys.path.insert(1, '/home/phil/Documents/Code/the-blue-alliance')
    sys.path.insert(1, '/home/phil/Documents/Code/the-blue-alliance/lib')
except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

from google.appengine.ext.remote_api import remote_api_stub
from models.event import Event
from database.match_query import EventMatchesQuery
from helpers.match_helper import MatchHelper
from helpers.match_manipulator import MatchManipulator
from helpers.match_time_prediction_helper import MatchTimePredictionHelper


def get_schedule_error(match):
    if match.actual_time and match.time:
        if match.actual_time > match.time:
            # Early
            delta = match.actual_time - match.time
            s = int(delta.total_seconds())
            return s
        elif match.time > match.actual_time:
            # Late
            delta = match.time - match.actual_time
            s = int(delta.total_seconds())
            return -1 * s
        else:
            return 0


def get_prediction_error(match):
    if match.actual_time and match.predicted_time:
        if match.actual_time > match.predicted_time:
            # Early
            delta = match.actual_time - match.predicted_time
            s = int(delta.total_seconds())
            return s
        elif match.predicted_time > match.actual_time:
            # Late
            delta = match.predicted_time - match.actual_time
            s = int(delta.total_seconds())
            return -1 * s
        else:
            return 0


def main(args):
    # First, get the event's qual matches and wipe scores. No cheating!
    event = Event.get_by_id(args.event)
    if not event:
        print "Event {} not found".format(args.event)
        return

    organized = MatchHelper.organizeMatches(event.matches)
    matches = organized['qm']

    print "Found {} qual matches".format(len(matches))

    # Now, go match by match and run predictions
    timezone = pytz.timezone(event.timezone_id)
    errors = []
    sched_errors = []
    last_match = None
    for i in range(0, len(matches) + 1):
        played_matches = matches[:i]
        unplayed_matches = matches[i:]
        # print "i={}: Found {} played/{} unplayed matches".format(i, len(played_matches), len(unplayed_matches))
        MatchTimePredictionHelper.predict_future_matches(event.key_name, played_matches, unplayed_matches, timezone, False, log=False)

        # Skip matches played out of sequence
        if last_match and (i == len(matches) or matches[i].actual_time > last_match.actual_time):
            last_match = matches[i - 1]
            errors.append(get_prediction_error(last_match))
            sched_errors.append(get_schedule_error(last_match))
            print "Error in predicting {}: {}".format(last_match.short_name, last_match.prediction_error_str)

        if i < len(matches):
            last_match = matches[i]

    os.chdir(start)
    with open('{}_cycles.csv'.format(args.event), 'w') as csvfile:
        writer = csv.writer(csvfile)
        for i, error in enumerate(errors):
            writer.writerow([i, error, sched_errors[i]])


def local_auth_func():
    # Credentials don't matter on the local devserver
    return 'user', 'pass'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test TBA Time Predictions")
    parser.add_argument("--url", help="URL of GAE Remote API", required=True)
    parser.add_argument("--event", help="Event Key to test", required=True)
    args = parser.parse_args()

    print "Configuring GAE Remote API on {}".format(args.url)
    if 'localhost' in args.url:
        remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', local_auth_func, args.url)
    else:
        remote_api_stub.ConfigureRemoteApiForOAuth(url, '/_ah/remote_api')

    main(args)
