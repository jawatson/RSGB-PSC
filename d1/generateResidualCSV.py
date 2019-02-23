#!/usr/bin/python3

"""
A short script based on the "Create Difference Table Between Two CSV Files ver 3.00.py"
script included with the hfcomp suite of applications.  This version
has been modified to accept command line arguments.

USAGE:

python3 createDifferenceCSV.py predicted_data.csv measured_data.csv 

"""

import os
import datetime
import sys

if len(sys.argv) != 3:
    print("USAGE:")
    print("python3 createDifferenceCSV.py predicted_data.csv measured_data.csv")
    sys.exit(1)

fname1 = sys.argv[1]
fname2 = sys.argv[2]
fname3 = "residuals.csv"

print("Reading predicted values from: {:s}".format(fname1))
print("Reading measured valuess: {:s}".format(fname2))

if os.path.exists(fname1) and os.path.exists(fname2):
    f1 = open(fname1, "r")
    f2 = open(fname2, "r")
    f3 = open(fname3, "wt")

    line1 = f1.readline().strip('\n')
    line2 = f2.readline()

    f3.write(line1 + "\n")
    for row in f1:
        row = row.split(",")
        row2 = f2.readline()
        row2 = row2.split(",")

        outstr = ""
        for x in range(0,36):
                if x == 9:
                        if row[x] == row2[x]:
                                outstr = outstr + row[x]
                        else:
                                outstr = outstr + "diff: " + str(int(row[x]) - int(row2[x]))
                elif x > 11:
                        if float(row[x]) < -99: row[x] = "-99"     # Clamps The Minimum dB to -99
                        if float(row2[x]) < -99: row2[x] = "-99"     # Clamps The Minimum dB to -99
                        if float(row2[x]) == 999 or float(row[x]) == 999:
                                outstr = outstr + " (error)"
                        elif float(row2[x]) == 99 or float(row[x]) == 99:
                                outstr = outstr + "NO_DATA"
                        else:
                                diff = float(row[x]) - float(row2[x])
                                outstr = outstr + "{:.2f}".format(diff)
                else:
                        outstr = outstr + row[x]
                if x < 35: outstr = outstr + ","
        f3.write(outstr + "\n")
    f3.close()
    f2.close()
    f1.close()

print("Written residuals to {:s}".format(f3.name))
