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
Create radcom style Predictions
"""

"""
Uses the pysolar package to determine the sun's positionself.
On Ubuntu this is installed with;
sudo apt install python3-pysolar
"""

import csv
import datetime
import math
import os
import subprocess
from tempfile import NamedTemporaryFile


target_zones = [{"id":"4U1UN", "location":"New York City", "entity":"United Nations", "lat":"40.750", "lng":"-74.000"},
          {"id":"VE8AT", "location":"Eureka, Nunavut", "entity":"Canada", "lat":"79.958", "lng":"-86.000"},
          {"id":"W6WX", "location":"Mt. Umunhum", "entity":"United States", "lat":"37.125", "lng":"-121.917"},
          {"id":"KH6RS", "location":"Maui", "entity":"Hawaii", "lat":"20.750", "lng":"-156.417"},
          {"id":"ZL6B", "location":"Masterton", "entity":"New Zealand", "lat":"-41.083", "lng":"175.583"},
          {"id":"VK6RBP", "location":"Rolystone", "entity":"Australia", "lat":"-32.125", "lng":"116.000"},
          {"id":"JA2IGY", "location":"Mt. Asama", "entity":"Japan", "lat":"34.417", "lng":"136.750"},
          {"id":"RR9O", "location":"Novosibirsk", "entity":"Russia", "lat":"54.958", "lng":"82.833"},
          {"id":"VR2B", "location":"Hong Kong", "entity":"Hong Kong", "lat":"22.250", "lng":"114.083"},
          {"id":"4S7B", "location":"Colombo", "entity":"Sri Lanka", "lat":"6.875", "lng":"79.833"},
          {"id":"ZS6DN", "location":"Pretoria", "entity":"South Africa", "lat":"-25.917", "lng":"28.250"},
          {"id":"5Z4B", "location":"Kariobangi", "entity":"Kenya", "lat":"-1.25", "lng":"36.833"},
          {"id":"4X6TU", "location":"Tel Aviv", "entity":"Israel", "lat":"32.042", "lng":"34.750"},
          {"id":"OH2B", "location":"Lohja", "entity":"Finland", "lat":"60.000", "lng":"24.000"},
          {"id":"CS3B", "location":"São Jorge", "entity":"Madeira", "lat":"32.792", "lng":"-17.000"},
          {"id":"LU4AA", "location":"Buenos Aires", "entity":"Argentina", "lat":"-34.625", "lng":"-58.417"},
          {"id":"OA4B", "location":"Lima", "entity":"Peru", "lat":"-12.083", "lng":"-77.000"},
          {"id":"YV5B", "location":"Caracas", "entity":"Venezuela", "lat":"9.083", "lng":"-67.833"}
          ]


def run_radcom_predictions(tx_lat, tx_lng, path_ssn):
    radcom_predictions = {}
    for zone in target_zones:
        rx_lat = float(zone['lat'])
        rx_lng = float(zone['lng'])
        radcom_predictions[zone['id']] = {}
        radcom_predictions[zone['id']]['predictions'] = run_p2p_prediction(tx_lat, tx_lng, rx_lat, rx_lng, path_ssn, "/snap/iturhfprop/current/usr/share/iturhfprop/data/")
        radcom_predictions[zone['id']]['meta'] = {}
        radcom_predictions[zone['id']]['meta']['location'] = zone['location']
    return radcom_predictions


def get_predictions_as_dict(csv_file, parameters):
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
    return predictions


def run_p2p_prediction(tx_lat, tx_lng, rx_lat, rx_lng, path_ssn,
                    data_file_path,
                    path_name="",
                    tx_antenna="ISOTROPIC",
                    tx_gos=0.0,
                    rx_antenna="ISOTROPIC",
                    rx_gos=0.0,
                    path_month=None,
                    path_year=None,
                    path_hour='1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24',
                    tx_power=100,
                    path_sorl="SHORTPATH",
                    path_manmade_noise="CITY"
                    ):
    tx_power = 10 * (math.log10(tx_power)/1000)
    buf = []
    if path_name:
        buf.append('PathName "{:s}"'.format(path_name))
    buf.append('Path.L_tx.lat {:.6f}'.format(tx_lat))
    buf.append('Path.L_tx.lng {:.6f}'.format(tx_lng))
    buf.append('TXAntFilePath "{:s}"'.format(tx_antenna))
    if tx_antenna == "ISOTROPIC":
        buf.append('TXGOS {:.2f}'.format(tx_gos))

    buf.append('Path.L_rx.lat {:.6f}'.format(rx_lat))
    buf.append('Path.L_rx.lng {:.6f}'.format(rx_lng))
    buf.append('RXAntFilePath "{:s}"'.format(rx_antenna))
    if rx_antenna == "ISOTROPIC":
        buf.append('RXGOS {:.2f}'.format(rx_gos))

    if not path_year:
        now = datetime.datetime.utcnow()
        path_year = now.year
    buf.append('Path.year {:d}'.format(path_year))
    if not path_month:
        now = datetime.datetime.utcnow()
        path_month = now.month
    buf.append('Path.month {:d}'.format(path_month))

    buf.append('Path.hour {:s}'.format(path_hour))
    buf.append('Path.SSN {:d}'.format(path_ssn))
    buf.append('Path.frequency 28.85, 24.94, 21.225, 18.118, 14.175, 10.125, 7.1, 5.0, 3.65')
    buf.append('Path.txpower {:.2f}'.format(tx_power))
    buf.append('Path.BW 500.0')
    buf.append('Path.SNRr 3.0')
    buf.append('Path.SNRXXp 90')
    buf.append('Path.ManMadeNoise "{:s}"'.format(path_manmade_noise))
    buf.append('Path.SorL "{:s}"'.format(path_sorl))
    buf.append('RptFileFormat "RPT_BCR"')
    buf.append('LL.lat {:.6f}'.format(rx_lat))
    buf.append('LL.lng {:.6f}'.format(rx_lng))
    buf.append('LR.lat {:.6f}'.format(rx_lat))
    buf.append('LR.lng {:.6f}'.format(rx_lng))
    buf.append('UL.lat {:.6f}'.format(rx_lat))
    buf.append('UL.lng {:.6f}'.format(rx_lng))
    buf.append('UR.lat {:.6f}'.format(rx_lat))
    buf.append('UR.lng {:.6f}'.format(rx_lng))
    buf.append('DataFilePath "{:s}"'.format(data_file_path))

    input_file = NamedTemporaryFile(mode='w+t', prefix="proppy_", suffix='.in', delete=False)
    text_in = "{:s}\n".format('\n'.join(buf))
    #print(text_in)
    input_file.write(text_in)
    input_file.close()

    FNULL = open(os.devnull, 'w')
    output_file = NamedTemporaryFile(prefix="proppy_", suffix='.out', delete=False)
    print(input_file.name)
    print(output_file.name)

    return_code = subprocess.call(["ITURHFProp",
        '-s',
        '-c',
        input_file.name,
        output_file.name],
        stderr=subprocess.STDOUT)

    if return_code != 232:
        print(text_in)
        raise ITURHFPropError("Internal Server Error: Return Code {:d}".format(return_code))

    try:
        #prediction = REC533Out(output_file.name)
        #muf, mesh_grid, params = prediction.get_p2p_plot_data('BCR')
        #print(params.title)
        bcr_dict = get_predictions_as_dict(output_file.name, ['BCR',])
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise ITURHFPropError("Internal Server Error: Error parsing file")
    return bcr_dict

"""
Values in the range 0-100
"""
def get_colour(prediction):
    colour_map = ['#ffffff', '#00ffee', '#00ff5c', '#29ff00', '#afff00', '#ddff00', '#fcff00', '#ffe700', '#ffaf00', '#ff7100', '#ff0000']
    colour = colour_map[math.floor(prediction/10.0)]
    return colour


def get_html_table(json_data, parameter):
    buf = []
    buf.append('<table><tr><th>&nbsp;</th><th colspan=24>'+json_data['meta']['location']+'</th></tr>')
    buf.append('<tr><th>&nbsp;</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th></tr>')
    for freq, predictions in json_data['predictions'].items():
        buf.append('<tr><td>{:s}</td>'.format(freq))
        for prediction in predictions[parameter]:
            buf.append('<td bgcolor="{:s}" title="BCR={:s}%"></td>'.format(get_colour(float(prediction)), prediction))
        buf.append('</tr>')
    return buf


if __name__ == "__main__":
    path_ssn = 4
    json_data = run_radcom_predictions(45.0, 1.5, path_ssn)
    html_doc = []
    html_doc.append('<html>')
    html_doc.append('<meta name="viewport" content="width=device-width, initial-scale=1"><title>DX Charts</title>')
    html_doc.append('<style type="text/css">body { font-family: sans-serif; font-size: x-small; -webkit-print-color-adjust: exact; } table, th, td { border: 1px dotted black; border-collapse: collapse; font-size: x-small; } p { font-size: small; } p#h { font-size: x-small; }</style>')
    html_doc.append('<body>')
    for k,v in json_data.items():
        html_doc.append('<p>'+v['meta']['location']+'</p>')
        html_doc.extend(get_html_table(v, 'BCR'))
    html_doc.append('</body></html>')
    with open('radcom.html', 'w') as html_file:
        html_file.write("{:s}\n".format('\n'.join(html_doc)))
