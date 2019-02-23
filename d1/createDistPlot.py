"""
This script produces a graph showing the distribution of values from a csv
file produced by the hfmodelcomp suite of applications.  The script would
typically be used to produce plots similar to P.1148-1 (Figure 2) and
requires a file containing the difference between predicted and measured 
as input (i.e. produced by script '40').

The default values below bin the errors into 6dB chunks, centred about zero.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def rmse(residuals): 
    return np.sqrt(np.mean([i ** 2 for i in residuals]))
    #return np.sqrt(sum([i ** 2 for i in residuals]) / len(residuals))


# Constants
BIN_WIDTH = 6
CLIP_LOWER = -99.0
CLIP_UPPER = 99.0

values = []

if len(sys.argv) != 2:
    print("USAGE:")
    print("python3 createDifferenceCSV.py difference_table.csv")
    sys.exit(1)

df = pd.read_csv(sys.argv[1])

"""
Extract data for each hour as a series in which '(no data)' is converted to NaN,
which is then dropped from the series before conversion to a list.  The final
list ('values') contains only the numeric elements of the hourly predictions.
"""
for col in df.ix[:,'1:00':'24:00']:
    values.extend(pd.to_numeric(df[col], errors='coerce').dropna().tolist())

#print(values)

#Calculate the mean and std.dev before clipping...
count = len(values)
mean = np.mean(values)
std_dev = np.std(values)
rmse = rmse(values)

values = np.clip(values, CLIP_LOWER, CLIP_UPPER)

bin_limits = np.arange(CLIP_LOWER, CLIP_UPPER+BIN_WIDTH, BIN_WIDTH)

n, bins, patches = plt.hist(values, bin_limits, facecolor='green', alpha=0.5)

print("         Bin             Count")
print("-----------------------------------")
for bin_num in range(0, len(bin_limits)-1):
    percentage = 100 *(n[bin_num] / count)
    print("{:5.1f}dB <--> {:5.1f}dB: {:4.0f} ({:.1f}%)".format(bins[bin_num], bins[bin_num+1], n[bin_num], percentage))
print("\nMean: {:.2f} SD: {:.2f} RMSE: {:.2f}".format(mean, std_dev, rmse))

plt.ylim([0,5000])

plt.axvline(x=mean, color='r')
plt.axvline(x=mean-std_dev, ls='dashed', color='r')
plt.axvline(x=mean+std_dev, ls='dashed', color='r')

plt.xlabel('Error (dB)'.format(len(values), mean, std_dev))
plt.ylabel('Count')
plt.title('Predicted vs. Measured Field Strength')
bbox_props = dict(fc="white", ec="k", lw=1)
summary = "Count = {:d}\nMean = {:.2f}\n$\sigma$ = {:.2f}".format(count, mean, std_dev)
plt.text(-90,3400, summary, bbox=bbox_props)
plt.show()
