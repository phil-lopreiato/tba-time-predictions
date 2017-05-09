#! /bin/env python

import argparse
import collections
import csv
import pytz
import sys
import os

from datetime import timedelta

start = os.getcwd()
os.chdir('/home/phil/Documents/Code/the-blue-alliance')
try:
    import dev_appserver
    dev_appserver.fix_sys_path()
    sys.path.insert(1, '/home/phil/Documents/Code/the-blue-alliance')
    sys.path.insert(1, '/home/phil/Documents/Code/the-blue-alliance/lib')
except ImportError:
    print('Please make sure the App Engine SDK is in your PYTHONPATH.')
    raise

from google.appengine.ext.remote_api import remote_api_stub
from database.event_query import EventListQuery
from helpers.match_helper import MatchHelper
from helpers.match_time_prediction_helper import MatchTimePredictionHelper


def calculate_cycles(timezone, matches):
    cycles = collections.defaultdict(int)
    for i in range(1, len(matches)):
        last_match = matches[i - 1]
        next_match = matches[i]

        if not last_match.time or not next_match.time:
            continue
        last_schedule = MatchTimePredictionHelper.as_local(last_match.time, timezone)
        next_schedule = MatchTimePredictionHelper.as_local(next_match.time, timezone)

        if not last_match.actual_time or not last_match.actual_time:
            continue
        last_actual = MatchTimePredictionHelper.as_local(last_match.actual_time, timezone)
        next_actual = MatchTimePredictionHelper.as_local(next_match.actual_time, timezone)

        # If there is a day gap, skip this cycle
        if last_schedule.day != next_schedule.day:
            continue

        # If there is a >= 10 minute schedule gap, this is likely some break
        if (next_schedule - last_schedule) >= timedelta(minutes=10):
            continue

        # If these matches were played out of sequence, skip
        if last_actual > next_actual:
            continue

        # Catch another case of out of sequence
        if i + 1 < len(matches):
            next_next_match = matches[i + 1]
            next_next_actual = MatchTimePredictionHelper.as_local(next_next_match.actual_time, timezone)
            if next_actual > next_next_actual:
                continue

        cycle_in_seconds = MatchTimePredictionHelper.timestamp(next_actual) - MatchTimePredictionHelper.timestamp(last_actual)
        cycles[cycle_in_seconds] += 1

    return cycles


def main(args):
    events = EventListQuery(args.year).fetch()
    hist = collections.defaultdict(int)
    for event in events:
        if not event.timezone_id:
            print "No timezone for {}, skipping...".format(event.key_name)
            continue
        timezone = pytz.timezone(event.timezone_id)
        matches = event.matches
        played_matches = MatchHelper.recentMatches(matches, num=0)
        matches_by_type = MatchHelper.organizeMatches(played_matches)
        cycles = calculate_cycles(timezone, matches_by_type[args.level])
        for time, count in cycles.iteritems():
            hist[time] += count

    os.chdir(start)
    with open('cycles.csv', 'w') as csvfile:
        ordered = collections.OrderedDict(sorted(hist.items()))
        writer = csv.writer(csvfile)
        writer.writerow(['Cycle Time', 'Frequency'])
        print ordered
        for k, v in ordered.iteritems():
            writer.writerow([k, v])


def local_auth_func():
    # Credentials don't matter on the local devserver
    return 'user', 'pass'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a histogram of match cycle times for a given year")
    parser.add_argument("--url", help="URL of GAE Remote API", required=True)
    parser.add_argument("--year", help="Year of events to test", type=int, default=2017)
    parser.add_argument("--level", help="Comp Level of matches to use", choices=['qm', 'qf', 'sf', 'f'], default='qm')
    args = parser.parse_args()

    print "Configuring GAE Remote API on {}".format(args.url)
    if 'localhost' in args.url:
        remote_api_stub.ConfigureRemoteApi(None, '/_ah/remote_api', local_auth_func, args.url)
    else:
        remote_api_stub.ConfigureRemoteApiForOAuth(url, '/_ah/remote_api')

    main(args)
