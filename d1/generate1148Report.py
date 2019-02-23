"""
MIT License

Copyright (c) 2019 James Watson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


"""
Short script to produce Box plots from a difference file for the
sub-groups identified by the ITU P.1148;

https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.1148-1-199705-I!!PDF-E.pdf

"""

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

# Earth radius
R0 = 6371.0
GeoMagPolelat = math.radians(78.5)
GeoMagPolelng = math.radians(-68.2)

#######################################
# This function originally appeared in the ITU suite of scripts
#######################################
def eot(month, day=15):
        doty = [ 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334 ]
        #D2R = math.pi/180.0

        # Earth's mean angular orbital velocity
        W = math.radians(360.0/365.24) # radians

        # The angle the earth has moved in it's orbit from the December solstice to date D
        # the approximate number of days between the Dec solstice and Jan 1st is 10 days
        D = doty[month-1] + day
        A = W*(D + 10) # radians

        # The angle the Earth has moved from the Dec solstice, including the correction for the Earth's orbital eccentricity, 0.0167
        # The number 12 is the number of days from the solstice to the Earth's perihelion
        B = A + (0.0167*math.sin(A - (12.0*W)))

        # The difference between the angles moved and the mean speed
        C = (A - math.atan2(math.tan(B), math.cos(math.radians(23.44))))/math.pi

        # The equation of time is then
        return(4.0*math.pi*(C - (int(C + 0.5)))) # minutes


def mode_sort_key(item):
    key = 0
    m = 0
    p = 0
    prec = 10
    while (len(item) > 0):
        if item[0].isdigit():
            m = int(item[0])
            item = item[1:]
        else:
            m = 1
        if item.startswith('E'):
            p = 10
            item = item[1:]
        elif item.startswith('F1'):
            p = 20
            item = item[2:]
        elif item.startswith('F2'):
            p = 30
            item = item[2:]
        else:
            item = item[1:]
        key = key + prec*(m+p)
        prec = 0
    return key

def get_subgroups(df, field, limits):
    vals = []
    for limit in limits:
        subgroup = df.loc[((abs(df[field]) > limit[0]) & (abs(df[field]) <= limit[1])), 'er_0100':'er_2400'].values.ravel()
        vals.append(subgroup[np.logical_not(np.isnan(subgroup))])
    return vals


def get_abs_subgroups(df, field, limits):
    vals = []
    for limit in limits:
        subgroup = df.loc[((df[field] > limit[0]) & (df[field] <= limit[1])), 'er_0100':'er_2400'].values.ravel()
        vals.append(subgroup[np.logical_not(np.isnan(subgroup))])
    return vals


def get_season_subgroups(df, field, seasons):
    vals = []
    for season in seasons:
        subgroup = df.loc[((df['mid_lat'] >= 0) & (df['month'].isin(season[0]))) | ((df['mid_lat'] < 0) & (df['month'].isin(season[1]))), 'er_0100':'er_2400'].values.ravel()
        vals.append(subgroup[np.logical_not(np.isnan(subgroup))])
    return vals


def midPoint(row):
    # Find the path mid point
    tx_lat = math.radians(row['tx_lat'])
    tx_lng = math.radians(row['tx_lng'])
    rx_lat = math.radians(row['rx_lat'])
    rx_lng = math.radians(row['rx_lng'])
    d = row['distance']/R0
    A = math.sin(0.5*d)/math.sin(d)
    B = math.sin(0.5*d)/math.sin(d)
    x = A*math.cos(tx_lat)*math.cos(tx_lng) +  B*math.cos(rx_lat)*math.cos(rx_lng)
    y = A*math.cos(tx_lat)*math.sin(tx_lng) +  B*math.cos(rx_lat)*math.sin(rx_lng)
    z = A*math.sin(tx_lat) +  B*math.sin(rx_lat)
    mid_lat = math.atan2(z,math.sqrt(math.pow(x,2)+math.pow(y,2)))
    mid_lng = math.atan2(y,x)
    gm_mid_lat = math.fabs(math.asin(math.sin(mid_lat)*math.sin(GeoMagPolelat) + math.cos(mid_lat)*math.cos(GeoMagPolelat)*math.cos(mid_lng - GeoMagPolelng)));

    return pd.Series({'mid_lat': math.degrees(mid_lat),
                        'mid_lng': math.degrees(mid_lng),
                        'gm_mid_lat':math.degrees(gm_mid_lat)})

clean_lat = lambda lat: float(lat[:-1]) if lat.endswith('N') else float('-'+lat[:-1])
clean_lng = lambda lng: float(lng[:-1]) if lng.endswith('E') else float('-'+lng[:-1])

#######################################################################
# START
#######################################################################

if len(sys.argv) not in (2, 3):
    print("USAGE:")
    print("python3 create1148BoxPlots.py residual_table.csv mode_table.csv")
    sys.exit(1)

do_mode_analysis = True if len(sys.argv)==3 else False

df = pd.read_csv(sys.argv[1], na_values='NO_DATA')
df.columns = ["id", "tx", "rx", "freq", "tx_lat", "tx_lng", "rx_lat", "rx_lng", "distance", "ssn", "year", "month", "er_0100", "er_0200", "er_0300", "er_0400", "er_0500", "er_0600", "er_0700", "er_0800", "er_0900", "er_1000", "er_1100", "er_1200", "er_1300", "er_1400", "er_1500", "er_1600", "er_1700", "er_1800", "er_1900", "er_2000", "er_2100", "er_2200", "er_2300", "er_2400"]

df['tx_lat'] = df['tx_lat'].apply(clean_lat)
df['tx_lng'] = df['tx_lng'].apply(clean_lat)
df['rx_lat'] = df['rx_lat'].apply(clean_lat)
df['rx_lng'] = df['rx_lng'].apply(clean_lat)

if do_mode_analysis:
    old_fields = ['{:d}:00'.format(v) for v in range(1, 24)]
    old_fields.append('24:00:00')
    new_fields = ['m_{:0>2d}00'.format(v) for v in range(1, 25)]
    mode_df = pd.read_csv(sys.argv[2], usecols=old_fields)
    mode_df.columns = new_fields
    df = pd.concat([df, mode_df], axis=1)

mid_points_df = df.apply (lambda row: midPoint (row),axis=1)
df = pd.concat([df, mid_points_df], axis=1)

df.to_csv('p1148.csv')
str_buf = []
str_buf.append("{:30s}{:>10s}{:>10s}{:>10s}".format("", "Count", "Mean", "SD"))

##################################
# FREQUENCY
##################################
groups = [(2, 5), (5, 10), (10, 15), (15, 30)]
box_data = get_subgroups(df, 'freq', groups)
labels = ["{:d}-{:d}MHz\n({:d})".format(g[0], g[1],len(s)) for g,s in zip(groups, box_data)]

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Frequency Group')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('freq.png')
plt.clf()

str_buf.append("Frequency groups (MHz):")
for g,s in zip(groups, box_data):
    str_buf.append("{:>5d} \u2264 f < {:<18d}{:>10d}{:>10.2f}{:>10.2f}".format(g[0], g[1], len(s), np.mean(s), np.std(s)))

##################################
# DISTANCE
##################################

groups =[(0, 1000), (1000, 2000), (2000, 3000),
        (3000, 4000), (4000, 5000), (5000, 7000),
        (7000, 9000), (9000, 12000), (12000, 15000),
        (15000, 18000), (18000, 22000), (22000, 40000)]
box_data = get_subgroups(df, 'distance', groups)
labels = ["{:d}-\n{:d}\n({:d})".format(g[0], g[1],len(s)) for g,s in zip(groups, box_data)]

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Distance Group')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('dist.png')
plt.clf()

str_buf.append("\nDistance (km):")
for g,s in zip(groups, box_data):
    if len(s):
        str_buf.append("{:>5d} \u2264 d < {:<18d}{:>10d}{:>10.2f}{:>10.2f}".format(g[0], g[1], len(s), np.mean(s), np.std(s)))
    else:
        str_buf.append("{:>5d} \u2264 d < {:<18d}{:>10d}{:>10s}{:>10s}".format(g[0], g[1], len(s), '---', '---'))

##################################
# GEO LATITUDE
##################################

groups =[(0, 20), (20, 40), (40, 60), (60, 90)]
box_data = get_abs_subgroups(df, 'gm_mid_lat', groups)
labels = ["{:d}-{:d}\n({:d})".format(g[0], g[1],len(s)) for g,s in zip(groups, box_data)]

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Geo Latitude')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('geolat.png')
plt.clf()


str_buf.append("\nGeomagnetic latitude (degrees) at path midpoint:")
for g,s in zip(groups, box_data):
    range_str = "".format(g[0], g[1])
    str_buf.append("{:>2d}\u00B0 \u2264 \u03D5 \u2264 {:<2d}\u00B0{:<17s}{:>10d}{:>10.2f}{:>10.2f}".format(g[0], g[1], "", len(s), np.mean(s), np.std(s)))


##################################
# SSN
##################################

groups =[(0, 15), (15, 45), (45, 75), (75, 105), (105, 150), (150, 300)]
box_data = get_subgroups(df, 'ssn', groups)
labels = ["{:d}-{:d}\n({:d})".format(g[0], g[1],len(s)) for g,s in zip(groups, box_data)]

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('SSN Group')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('ssn.png')
plt.clf()

str_buf.append("\nSunspot number:")
for g,s in zip(groups, box_data):
    str_buf.append("{:>3d} \u2264 R12 < {:<18d}{:>10d}{:>10.2f}{:>10.2f}".format(g[0], g[1], len(s), np.mean(s), np.std(s)))



##################################
# SEASONS
##################################

# Winter, Spring, Summer, Autumn
# Tuples for the Northern Hemisphere and the Southern
label_str = ['Winter', 'Spring', 'Summer', 'Autumn']
groups =[((11, 12, 1, 2), (5, 6, 7, 8)), ((3, 4), (9, 10)), ((5, 6, 7, 8), (11, 12, 1, 2)), ((9, 10), (3, 4))]
box_data = get_season_subgroups(df, 'month', groups)
labels = ["{:s}\n({:d})".format(g, len(s)) for g,s in zip(label_str, box_data)]

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Season (at path midpoint)')
plt.ylabel('Residual (dB)')

plt.savefig('seasons.png')
plt.clf()

str_buf.append("\nSeason at path midpoint:")
for g,s in zip(label_str, box_data):
    str_buf.append("{:<25s}{:>15d}{:>10.2f}{:>10.2f}".format(g, len(s), np.mean(s), np.std(s)))


##################################
# LOCAL TIME AT MID-POINT
##################################

str_buf.append("\nLocal time at path midpoint (h):")

# Use 1-24 to avoid confusion
vals = [[] for i in range(24)]
hour_step = 4
box_data = []
labels = ["{:d}-{:d}".format(h, h+hour_step) for h in range(0, 24, hour_step)]

for index, row in df.iterrows():
    #print("Lng: {:.2f}".format(row['mid_lng']))
    ltimeoffset = eot(row['month'])/60.0 + (row['mid_lng']/15.0)
    for colname, col in row['er_0100':'er_2400'].iteritems():
        #print("{:.2f} {:.2f}".format(float(colname[3:5]), ltimeoffset))
        ltime = float(colname[3:5]) + ltimeoffset
        if(ltime > 24):
            ltime = ltime - 24
        elif(ltime <= 0):
            ltime = ltime + 24
        if not math.isnan(col):
            vals[math.floor(ltime)].append(col)

for h in range(0, 24, hour_step):
    sample = [item for sublist in vals[h:h+hour_step] for item in sublist]
    str_buf.append(">{:0>2d}00-{:0>2d}00{:>30d}{:>10.2f}{:10.2f}".format(h, h+hour_step,
                                                                    len(sample),
                                                                    np.mean(sample),
                                                                    np.std(sample)))
    box_data.append(sample)

plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Local time at path midpoint (h)')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('local_time.png')
plt.clf()


##################################
# MODES
##################################

if do_mode_analysis:
    str_buf.append("\nModes (Paths < 7000km):")
    modes = pd.unique(df.loc[(df['distance'] < 7000),'m_0100':'m_2400'].values.ravel()).tolist()
    modes = sorted(modes, key=mode_sort_key)
    mode_residuals = []
    for mode in modes:
        vals = []
        for utc in range(1, 24+1):
            er_col_name = 'er_{:0>2d}00'.format(utc)
            m_col_name = 'm_{:0>2d}00'.format(utc)
            subgroup = df.loc[(df[m_col_name]==mode) & (df['distance'] < 7000)][er_col_name].values.ravel().tolist()
            vals = vals + subgroup
        str_buf.append("Mode: {:<24s}{:>10d}{:>10.2f}{:>10.2f}".format(mode,
                                                                        np.count_nonzero(~np.isnan(vals)),
                                                                        np.nanmean(vals),
                                                                        np.nanstd(vals)))
    """
    print("modes in the range 3-4000km")
    str_buf.append("\nModes (Paths < 7000km):")
    modes = pd.unique(df.loc[(df['distance'] > 3000) & (df['distance'] <= 4000),'m_0100':'m_2400'].values.ravel()).tolist()
    modes = sorted(modes, key=mode_sort_key)
    mode_residuals = []
    for mode in modes:
        vals = []
        for utc in range(1, 24+1):
            er_col_name = 'er_{:0>2d}00'.format(utc)
            m_col_name = 'm_{:0>2d}00'.format(utc)
            subgroup = df.loc[(df[m_col_name]==mode) & (df['distance'] > 3000) & (df['distance'] <= 4000)][er_col_name].values.ravel().tolist()
            vals = vals + subgroup
        print("Mode: {:<24s}{:>10d}{:>10.2f}{:>10.2f}".format(mode,
                                                                        np.count_nonzero(~np.isnan(vals)),
                                                                        np.nanmean(vals),
                                                                        np.nanstd(vals)))
    """

    #ITURHFProp doesn't include modes for paths > 7000km.  If thre are no
    # modes then skip this section
    if len(pd.unique(df.loc[(df['distance'] >= 7000),'m_0100':'m_2400'].values.ravel()).tolist()) > 1:
        str_buf.append("\nModes (All Paths):")
        modes = pd.unique(df.loc[:,'m_0100':'m_2400'].values.ravel()).tolist()
        modes = sorted(modes, key=mode_sort_key)
        mode_residuals = []
        for mode in modes:
            #print(mode)
            vals = []
            for utc in range(1, 24+1):
                er_col_name = 'er_{:0>2d}00'.format(utc)
                m_col_name = 'm_{:0>2d}00'.format(utc)
                subgroup = df.loc[df[m_col_name]==mode][er_col_name].values.ravel().tolist()
                #print(subgroup)
                vals = vals + subgroup
            str_buf.append("Mode: {:<24s}{:>10d}{:>10.2f}{:>10.2f}".format(mode,
                                                                        np.count_nonzero(~np.isnan(vals)),
                                                                        np.nanmean(vals),
                                                                        np.nanstd(vals)))

##################################
# DATA ORIGIN
##################################

str_buf.append("\nOrigin of Data:")
data_origin_dict = {'Germany':(8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24,
                        25, 26, 27, 28, 29, 30, 41, 42, 43, 44, 50, 72, 75, 76, 94,
                        95, 96, 97, 98, 99, 103, 104, 105, 106, 107, 111, 112, 113,
                        114, 115, 116, 131, 132, 133, 134, 135, 137, 138, 139, 142,
                        143, 144, 145, 161, 162, 163, 164, 165, 166, 167, 168, 170,
                        171, 172, 173, 175, 176, 177, 178),
                'Japan':(3, 4, 5, 6, 33, 102, 136, 152, 157, 158, 159, 160, 180, 181),
                'China':(31, 34, 35, 36, 37, 38, 39, 40, 45, 46, 47, 62, 63, 64, 65,
                        66, 80, 81, 82, 83, 108, 120, 122, 123, 124, 125, 149),
                'India':(2, 7, 32, 49, 52, 53, 54, 55, 58, 59, 61, 67, 68, 69, 70, 77,
                        78, 79, 117, 118, 128, 150),
                'Deutsche Welle':(1, 14, 15, 51, 73, 74, 90, 91, 92, 129, 130, 148,
                        174),
                'BBC/EBU':(56, 57, 60, 71, 84, 85, 86, 87, 88, 89, 93, 100, 101, 109,
                        110, 119, 121, 126, 127, 140, 141, 146, 147, 151, 153, 154,
                        155, 156, 169, 179),
                'Australia':(48,)}

box_data = []
labels = []
for origin, id_list in data_origin_dict.items():
    subgroup = df.loc[df['id'].isin(id_list), 'er_0100':'er_2400'].values.ravel()
    box_data.append(subgroup[np.logical_not(np.isnan(subgroup))])
    labels.append(origin)
    str_buf.append("{:<30s}{:>10d}{:>10.2f}{:>10.2f}".format(origin,
                                                        np.count_nonzero(~np.isnan(subgroup)),
                                                        np.nanmean(subgroup),
                                                        np.nanstd(subgroup)))


plt.boxplot(box_data, showmeans=True, labels=labels)
plt.axhline(y=0, color='r')
plt.ylim(-80, 80)
plt.xlabel('Origin of data')
plt.ylabel('Residual (dB)')
plt.tight_layout()
plt.savefig('origin.png')
plt.clf()

##################################
# ALL DISTANCES
##################################

groups =[(0, 40000)]
summary_vals = get_subgroups(df, 'distance', groups)[0]
str_buf.append('-' * 60)
str_buf.append("{:<30}{:>10d}{:>10.2f}{:>10.2f}".format("All data:",
                                                        len(summary_vals),
                                                        np.mean(summary_vals),
                                                        np.std(summary_vals)))
str_buf.append('-' * 60)

##################################
# PATHS / FREQUENCIES
##################################

str_buf.append("\nPath / Frequency Combinations:")
for name, group in df.groupby(['tx', 'rx', 'freq']):
    #print(name)
    er_values = group.loc[:,'er_0100':'er_2400'].values.ravel()
    str_buf.append("{:<15s}{:<15s}{:>4.1f}{:>6d}{:>10.2f}{:>10.2f}".format(name[0],
                                                                    name[1],
                                                                    name[2],
                                                                    np.count_nonzero(~np.isnan(er_values)),
                                                                    np.nanmean(er_values),
                                                                    np.nanstd(er_values)))




##################################
report_str = "{:s}\n".format('\n'.join(str_buf))
print(report_str.replace(' nan', ' ---'))
