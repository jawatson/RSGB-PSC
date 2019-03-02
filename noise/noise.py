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
Invesitgate the contibution of the atmospheric, galactic and man-made noise 
sources.  Uses the folowing RPT format cards.
RPT_NOISESOURCES		Noise (Atmospheric) FaA, (Man-made) FaM & (Galactic) FaG (dB)
RPT_NOISETOTAL			Total Noise, FamT (dB)
"""

import csv
import datetime
from math import log10
from operator import sub
import os
import subprocess
from tempfile import NamedTemporaryFile

target_zones = [{"id":"UA_MOSCOW", "location":"UA Moscow", "path":"SHORTPATH", "lat":55.7558, "lng":37.6173},
        {"id":"UA_YAKUTSK", "location":"UA Yakutsk, Siberia", "path":"SHORTPATH", "lat":62.0355, "lng":129.6755},
        {"id":"JA", "location":"JA Tokyo", "path":"SHORTPATH", "lat":35.6895, "lng":139.6917},
        {"id":"9V", "location":"9V Singapore", "path":"SHORTPATH", "lat":1.3521, "lng":103.8198},
        {"id":"VU", "location":"VU Hyderabad", "path":"SHORTPATH", "lat":18.3850, "lng":78.4867},
        {"id":"4X", "location":"4X Tel Aviv", "path":"SHORTPATH", "lat":32.0853, "lng":34.7818},
        {"id":"ZL_SP", "location":"ZL Wellington (SP)", "path":"SHORTPATH", "lat":-41.2865, "lng":174.7762},
        {"id":"ZL_LP", "location":"ZL Wellington (LP)", "path":"LONGPATH", "lat":-41.2865, "lng":174.7762},
        {"id":"PERTH", "location":"VK Perth", "path":"SHORTPATH", "lat":-31.9505, "lng":115.8605},
        {"id":"SYDNEY", "location":"VK Sydney", "path":"SHORTPATH", "lat":-33.8688, "lng":151.2093},
        {"id":"MELBOURNE_SP", "location":"VK Melbourne (SP)", "path":"SHORTPATH", "lat":-37.8136, "lng":144.9631},
        {"id":"MELBOURNE_LP", "location":"VK Melbourne (LP)", "path":"LONGPATH", "lat":-37.8136, "lng":144.9631},
        {"id":"KH6_SP", "location":"KH6 Honoloulu (SP)", "path":"SHORTPATH", "lat":21.3069, "lng":-157.8583},
        {"id":"KH6_lP", "location":"KH6 Honoloulu (LP)", "path":"LONGPATH", "lat":21.3069, "lng":-157.8583},
        {"id":"5W", "location":"5W Western Samoa", "path":"SHORTPATH", "lat":13.7590, "lng":172.1046},
        {"id":"3B8", "location":"3B8 Mauritius", "path":"SHORTPATH", "lat":-20.3484, "lng":57.5522},
        {"id":"ZS", "location":"ZS Johannesburg", "path":"SHORTPATH", "lat":-26.2041, "lng":28.0473},
        {"id":"5N", "location":"5N Ibadan", "path":"SHORTPATH", "lat":7.3775, "lng":3.9470},
        {"id":"5Z", "location":"5Z Nairobi", "path":"SHORTPATH", "lat":-1.2921, "lng":36.8219},
        {"id":"EA8", "location":"EA8 Canary Isles", "path":"SHORTPATH", "lat":28.2916, "lng":-16.6291},
        {"id":"LU", "location":"LU Buenos Aires", "path":"SHORTPATH", "lat":-34.6037, "lng":-58.3816},
        {"id":"PY", "location":"PY Rio de Janeiro", "path":"SHORTPATH", "lat":-22.9068, "lng":-43.1729},
        {"id":"OA", "location":"OA Lima", "path":"SHORTPATH", "lat":-12.0464, "lng":-77.0428},
        {"id":"YV", "location":"YV Caracas", "path":"SHORTPATH", "lat":10.4806, "lng":-66.9036},
        {"id":"TG", "location":"TG Guatamala", "path":"SHORTPATH", "lat":15.7835, "lng":-90.2308},
        {"id":"W_NEW_ORLEANS", "location":"W New Orleans", "path":"SHORTPATH", "lat":29.9511, "lng":-90.0715},
        {"id":"W_WASHINGTON_DC", "location":"W Washington DC", "path":"SHORTPATH", "lat":38.9072, "lng":-77.0369},
        {"id":"VE_QUEBEC", "location":"VE Quebec", "path":"SHORTPATH", "lat":52.9399, "lng":-73.5491},
        {"id":"KL_ANCHORAGE", "location":"KL Anchorage", "path":"SHORTPATH", "lat":61.2181, "lng":-149.9003},
        {"id":"VE_VANCOUVER", "location":"VE Vancouver", "path":"SHORTPATH", "lat":49.2827, "lng":-123.1207},
        {"id":"W_SAN_FANCISCO_SP", "location":"W San Francisco (SP)", "path":"SHORTPATH", "lat":37.7749, "lng":-122.4194},
        {"id":"W_SAN_FANCISCO_LP", "location":"W San Francisco (LP)", "path":"LONGPATH", "lat":37.7749, "lng":-122.4194}]



def run_noise_predictions(tx_lat, tx_lng, traffic, noise_level, path_ssn, path_month, path_year, data_path):
    predictions_list = []
    for zone in target_zones:
        rx_lat = float(zone['lat'])
        rx_lng = float(zone['lng'])
        predictions = run_p2p_prediction(tx_lat, tx_lng, rx_lat, rx_lng, path_ssn,
                path_frequency=[28.85, 24.94, 21.225, 18.118, 14.175, 10.125, 7.1, 5.33, 3.65],
                path_bw=traffic[0],
                path_SNRr=traffic[1],
                path_sorl=zone['path'],
                path_manmade_noise = noise_level,
                report_format=['RPT_NOISESOURCES', 'RPT_NOISETOTAL'],
                path_month=path_month,
                path_year=path_year,
                report_dict_keys=['FaM', 'FamT'],
                data_path=data_path,
                zeroMidnight=True)
        #print(predictions)
        meta = {}
        meta['location'] = zone['location']
        prediction = {'meta':meta,'predictions':predictions}
        predictions_list.append(prediction)
    return predictions_list


def get_predictions_as_dict(csv_file, parameters, zeroMidnight=False):
    predictions = {}
    with open(csv_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['frequency'] not in predictions:
                predictions[row['frequency']] = {}
                for parameter in parameters:
                    predictions[row['frequency']][parameter] = []
            for parameter in parameters:
                predictions[row['frequency']][parameter].append(row[parameter])

    if zeroMidnight:
        for freq, params in predictions.items():
            for param, preds in params.items():
                preds.insert(0, preds.pop())

    return predictions



def run_p2p_prediction(tx_lat, tx_lng, rx_lat, rx_lng, path_ssn,
                    path_name="",
                    tx_antenna="ISOTROPIC",
                    tx_gos=0.0,
                    rx_antenna="ISOTROPIC",
                    rx_gos=0.0,
                    path_month=None,
                    path_year=None,
                    path_hour=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
                    path_frequency=[10],
                    path_bw=3000,
                    path_SNRr=15,
                    tx_power=100,
                    path_sorl="SHORTPATH",
                    path_manmade_noise="CITY",
                    report_format=["RPT_BCR"],
                    data_path="./data/",
                    report_dict_keys=['BCR'],
                    zeroMidnight=False,
                    returnInputFile=False,
                    returnOutputFile=False
                    ):

    tx_power = 10 * (log10(tx_power/1000.0))

    report_format_str = " | ".join(report_format)
    path_frequency_str = ", ".join([str(n) for n in path_frequency])
    path_hour_str = ", ".join([str(n) for n in path_hour])
    buf = []
    if path_name:
        buf.append('PathName "{:s}"'.format(path_name))
    buf.append('Path.L_tx.lat {:.6f}'.format(tx_lat))
    buf.append('Path.L_tx.lng {:.6f}'.format(tx_lng))
    buf.append('TXAntFilePath "{:s}"'.format(tx_antenna))
    if tx_antenna == "ISOTROPIC":
        buf.append('TXGOS {:.2f}'.format(tx_gos))
    #buf.append('AntennaOrientation TX2RX')

    buf.append('Path.L_rx.lat {:.6f}'.format(rx_lat))
    buf.append('Path.L_rx.lng {:.6f}'.format(rx_lng))
    buf.append('RXAntFilePath "{:s}"'.format(rx_antenna))
    if rx_antenna == "ISOTROPIC":
        buf.append('RXGOS {:.2f}'.format(rx_gos))
    #buf.append('AntennaOrientation RX2TX')

    if not path_year:
        now = datetime.datetime.utcnow()
        path_year = now.year
    buf.append('Path.year {:d}'.format(path_year))
    if not path_month:
        now = datetime.datetime.utcnow()
        path_month = now.month
    buf.append('Path.month {:d}'.format(path_month))

    buf.append('Path.hour {:s}'.format(path_hour_str))
    buf.append('Path.SSN {:d}'.format(path_ssn))
    buf.append('Path.frequency {:s}'.format(path_frequency_str))
    buf.append('Path.txpower {:.2f}'.format(tx_power))
    buf.append('Path.BW {:.2f}'.format(path_bw))
    buf.append('Path.SNRr {:.2f}'.format(path_SNRr))
    buf.append('Path.SNRXXp 90')
    buf.append('Path.ManMadeNoise "{:s}"'.format(path_manmade_noise))
    buf.append('Path.SorL "{:s}"'.format(path_sorl))
    buf.append('RptFileFormat "{:s}"'.format(report_format_str))
    buf.append('LL.lat {:.6f}'.format(rx_lat))
    buf.append('LL.lng {:.6f}'.format(rx_lng))
    buf.append('LR.lat {:.6f}'.format(rx_lat))
    buf.append('LR.lng {:.6f}'.format(rx_lng))
    buf.append('UL.lat {:.6f}'.format(rx_lat))
    buf.append('UL.lng {:.6f}'.format(rx_lng))
    buf.append('UR.lat {:.6f}'.format(rx_lat))
    buf.append('UR.lng {:.6f}'.format(rx_lng))
    buf.append('DataFilePath "{:s}"'.format(data_path))

    input_file = NamedTemporaryFile(mode='w+t', prefix="proppy_", suffix='.in', delete=False)
    text_in = "{:s}\n".format('\n'.join(buf))
    #print(text_in)
    input_file.write(text_in)
    input_file.close()

    FNULL = open(os.devnull, 'w')
    output_file = NamedTemporaryFile(prefix="proppy_", suffix='.out', delete=False)

    return_code = subprocess.call(["ITURHFProp",
        '-c',
        input_file.name,
        output_file.name],
        stderr=subprocess.STDOUT)

    if return_code != 232:
        raise ITURHFPropError("Internal Server Error: Return Code {:d}".format(return_code))

    try:
        prediction_dict = get_predictions_as_dict(output_file.name, report_dict_keys, zeroMidnight=zeroMidnight)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise ITURHFPropError("Internal Server Error: Error parsing file")

    print(input_file.name)
    print(output_file.name)
    #os.remove(input_file.name)
    #os.remove(output_file.name)
    return prediction_dict


if __name__ == "__main__":
    path_ssn = 3
    traffic = (500, 0) # A tuple of (bandwidth, SNRr)
    path_month = 3
    path_year = 2019
    noise_level = 'RESIDENTIAL'
    data_path = "/home/jwatson/develop/proppy/flask/data/"
    json_data = run_noise_predictions(45.0, 1.5, traffic, noise_level, path_ssn, path_month, path_year, data_path)

    out_buf = []    #print(json_data)
    for location in json_data:
        out_buf.append("\n{:s}".format(location['meta']['location']))
        for idx, freq in enumerate(sorted(location['predictions'].keys(), key=float)):
            utc = list(range(0,24))
            fam = location['predictions'][freq]['FaM']
            famt = location['predictions'][freq]['FamT']
            delta = [float(a) - float(b) for a, b in zip(famt, fam)]
            out_buf.append("-"*180)
            out_buf.append((" Freq.   UTC" + (" {: >6d}")*24).format(*utc))
            out_buf.append(("{:>6s}  FamT" + (" {: >6s}")*24).format(freq, *famt))
            out_buf.append(("{:>6s}   FaM" + (" {: >6s}")*24).format(freq, *fam))
            out_buf.append(("{:>6s} delta" + (" {: >6.2f}")*24).format(freq, *delta))
    with open('noise.txt', 'w') as out_file:
        out_file.write("{:s}\n".format('\n'.join(out_buf)))
    
