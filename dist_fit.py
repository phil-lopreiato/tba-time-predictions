#! /bin/env python

import csv
import pylab
import matplotlib.pyplot as plt
import numpy as np
from lmfit.models import SkewedGaussianModel
from scipy.optimize import curve_fit
from scipy.misc import factorial
from scipy.stats import skewnorm


if __name__ == "__main__":
    cycles = []
    xvals = []
    yvals = []
    with open('cycles.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            cycle = row[0]
            freq = row[1]
            try:
                float(cycle)
            except ValueError:
                continue

            cycle = int(float(cycle))
            freq = int(float(freq))

            for i in range(freq):
                cycles.append(cycle)

            xvals.append(cycle)
            yvals.append(freq)

    # Plot cycle histogram
    plt.hist(cycles, bins=40, range=[300, 900])

    # Fit the cycles to a skewed normal pdf
    model = SkewedGaussianModel()
    params = model.make_params(amplitude=160000, center=400, sigma=120, gamma=5)
    result = model.fit(yvals, params, x=xvals)
    plt.plot(xvals, result.init_fit, 'r-')
    print result.fit_report()

    # Show plot
    plt.title('2017 Cycle Time Distribution')
    plt.ylabel('Frequency')
    plt.xlabel('Cycle Time (seconds)')
    axes = plt.gca()
    axes.set_xlim([300, 900])
    plt.savefig('2017cycles_trend.png')
