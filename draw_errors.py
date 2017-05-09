#! /bin/env python

import glob
import csv
import pylab
import matplotlib.pyplot as plt
import numpy as np
from lmfit.models import SkewedGaussianModel
from scipy.optimize import curve_fit
from scipy.misc import factorial
from scipy.stats import skewnorm


if __name__ == "__main__":
    files = glob.glob('2017*_cycles.csv')
    for data in files:
        print "Parsing {}".format(data)
        with open(data, 'r') as csvfile:
            xvals = []
            errors = []
            sched_errors = []
            event_key = data.split('_')[0]
            reader = csv.reader(csvfile)
            for row in reader:
                xvals.append(int(row[0]))
                errors.append(int(row[1]))
                sched_errors.append(int(row[2]))

            plt.clf()
            plt.plot(xvals, errors)
            plt.title('{} Time Prediction Errors'.format(event_key))
            plt.ylabel('Error (seconds)')
            plt.xlabel('Match')
            axes = plt.gca()
            axes.set_ylim([-100, min(max(errors), 4000)])
            plt.savefig('{}_error.png'.format(event_key))

            plt.clf()
            plt.plot(xvals, sched_errors)
            plt.title('{} Schedule Errors'.format(event_key))
            plt.ylabel('Error (seconds)')
            plt.xlabel('Match')
            axes = plt.gca()
            axes.set_ylim([min(sched_errors), min(max(sched_errors), 4000)])
            plt.savefig('{}_sched_error.png'.format(event_key))
