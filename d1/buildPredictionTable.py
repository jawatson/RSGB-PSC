"""
Copyright (c) <year> <copyright holders>

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

import copy
import csv
import math
import os
import subprocess

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
                    input_file_path = None,
                    output_file_path = None,
                    report_dict_keys=['BCR'],
                    zeroMidnight=False,
                    returnInputFile=False,
                    returnOutputFile=False
                    ):

    tx_power = 10 * (math.log10(tx_power/1000.0))

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

    if input_file_path:
        input_file = open(input_file_path, 'w')
    else:
        input_file = NamedTemporaryFile(mode='w+t', prefix="proppy_", suffix='.in', delete=False)
    text_in = "{:s}\n".format('\n'.join(buf))
    #print(text_in)
    input_file.write(text_in)
    input_file.close()

    FNULL = open(os.devnull, 'w')
    if output_file_path:
        output_file = open(output_file_path, 'w')
    else:
        output_file = NamedTemporaryFile(prefix="proppy_", suffix='.out', delete=False)
    #print(input_file.name)
    #print(output_file.name)

    return_code = subprocess.call(['ITURHFProp',
        '-c',
        input_file.name,
        output_file.name],
        stderr=subprocess.STDOUT)

    if return_code != 232:
        print('ITURHFPropError Return Code {:d}'.format(return_code))

    try:
        prediction_dict = get_predictions_as_dict(output_file.name, report_dict_keys, zeroMidnight=zeroMidnight)
    except:
        print("Internal Server Error: Error parsing file")

    if not input_file_path:
        os.remove(input_file.name)
    if not output_file_path:
        os.remove(output_file.name)
    return prediction_dict

def build_prediction_table():
    d1_fn = "d1_data_measured.csv"
    pr_fn = "d1_data_predicted.csv"
    working_dir = "run"


    with open(d1_fn,'r') as d1file, open(pr_fn,'w') as prediction_file:
        d_reader = csv.DictReader(d1file)
        headers = d_reader.fieldnames
        d_writer = csv.DictWriter(prediction_file, fieldnames=headers)
        d_writer.writeheader()
        for row in d_reader:
            path_name = "{:s} {:s} ".format(row['tx_name'], row['rx_name'])
            file_name = "{:s}_{:s}_{:s}_{:s}".format(row['id'], row['freq'], row['month'], row['year'])
            input_file_path = os.path.join(working_dir, file_name+'.in')
            output_file_path = os.path.join(working_dir, file_name+'.out')
            tx_lat = float(row['tx_lat'][:-1]) if row['tx_lat'][-1:] == 'N' else (-float(row['tx_lat'][:-1]))
            tx_lng = float(row['tx_lng'][:-1]) if row['tx_lng'][-1:] == 'E' else (-float(row['tx_lng'][:-1]))
            rx_lat = float(row['rx_lat'][:-1]) if row['rx_lat'][-1:] == 'N' else (-float(row['rx_lat'][:-1]))
            rx_lng = float(row['rx_lng'][:-1]) if row['rx_lng'][-1:] == 'E' else (-float(row['rx_lng'][:-1]))
            path_ssn = int(row['ssn'])
            p = run_p2p_prediction(tx_lat, tx_lng, rx_lat, rx_lng, path_ssn,
                                path_name=path_name,
                                tx_antenna="ISOTROPIC",
                                tx_gos=0.0,
                                rx_antenna="ISOTROPIC",
                                rx_gos=0.0,
                                path_month=int(row['month']),
                                path_year=1900 + int(row['year']),
                                path_hour=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
                                path_frequency=[float(row['freq'])],
                                path_bw=3000,
                                path_SNRr=15,
                                tx_power=1000,
                                path_sorl="SHORTPATH",
                                path_manmade_noise="CITY",
                                report_format=["RPT_E"],
                                data_path="./data/",
                                input_file_path = input_file_path,
                                output_file_path = output_file_path,
                                report_dict_keys=['Ep'],
                                zeroMidnight=False,
                                returnInputFile=False,
                                returnOutputFile=False
                                )
            #print(p)
            pred_dict = row
            freq_key = next(iter(p.items()))[0]
            for utc in range(1,25):
                utc_key = "{:d}:00".format(utc)
                pred_dict[utc_key] = p[freq_key]['Ep'][utc-1]
            d_writer.writerow(pred_dict)

def main():
    build_prediction_table()


if __name__ == "__main__":
    # execute only if run as a script
    main()
