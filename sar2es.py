#!/bin/python
"""
sar to Elasticsearch conversion script

This scripts reads reads Linux sysstats's sar text, converts it to JSON
and inserts into the specified Elasticsearch server


sar  example data:
Linux 3.10.0-693.17.1.el7.x86_64 (myhostname)         28-02-2018      _x86_64_        (4 CPU)
...
blank line
time header line
time data line
...
ignore lines starting with "Average"
"""

import sys
import os
import re
import subprocess
import time
from optparse import OptionParser
from time import strftime


def command_line_parser():
    parser = OptionParser()
    parser.add_option("-c", "--count", dest="count", default="1",
                      help="number of samples to collect", metavar="count")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="print debug messages")
    parser.add_option("-e", "--elasticsearch-url", dest="es_url", default="http://localhost:9200",
                      help="elastic search url for data upload", metavar="es_url")
    parser.add_option("-m", "--max-time", dest="max_time", default="3",
                      help="max time to wait for elasticsearch upload", metavar="max_time")
    parser.add_option("-i", "--interval", dest="interval", default="1",
                      help="set interval between data collections (seconds)", metavar="interval")

    (options, args) = parser.parse_args()
    return options, args


def get_status_output(command, input=None):
    input_handler = None
    if input is not None:
        input_handler = subprocess.PIPE
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=input_handler)

    out, err = process.communicate(input=input)
    return (process.returncode, out, err)


class SarDataParser:

    def __init__(self):
        self.metrics_info = None
        self.metrics_header = None
        self.metrics_data = []
        self.all_data = []
        self.json = ''

    def process(self, line):
        if line.startswith("Average"):
            return
        if line == "":
            if self.metrics_header is not None:
                # Process the data that was retrieved
                if len(self.metrics_data) == 1:
                    metric_name = 'system'
                    base_index = 1
                else:
                    metric_name = self.metrics_header[1]
                    base_index = 2
                # Ignore this type of data
                if self.metrics_header[1] in ["INTR", "BUS", "FAN", "TEMP"]:
                    self.metrics_header = None
                    self.metrics_data = []
                    return
                metric_name = metric_name.lower()
                for metric_record in self.metrics_data:
                    date = self.metrics_info[0][3]
                    timestamp_str = date+"T"+metric_record[0]
                    metrics = {}
                    for i in range(base_index, len(self.metrics_header)):
                        metrics[self.metrics_header[i]] = float(metric_record[i].replace(',', '.'))
                    json_record = {
                        'hostname': self.metrics_info[0][2],
                        '@timestamp': timestamp_str,
                        'metric_name': metric_name,
                        'component': metric_record[1]
                    }
                    json_record.update(metrics)

                    json_items = []
                    for key, value in json_record.iteritems():
                        if isinstance(value, basestring):
                            value = '"%s"' % value
                        json_items.append('"%s": %s' % (key, value))
                    json_str = '{%s}' % ', '.join(json_items)
                    date_stamp = strftime("%d-%m-%Y")
                    self.json += '{"index": {"_index": "sar-%s", "_type": "_doc" }}\n' % date_stamp
                    self.json += json_str + "\n"
            self.metrics_header = None
            self.metrics_data = []
        elif self.metrics_info is None:
            self.metrics_info = re.findall(r"(\S+)\s+(\S+)\s+\(([\w\.]+)\)\s+(\S+)", line)
        elif self.metrics_header is None:
            self.metrics_header = line.split()
        else:
            self.metrics_data.append(line.split())


def main():
    # Setup locale settings to get standard date/time formats
    os.environ['S_TIME_FORMAT'] = 'ISO'
    os.environ['LANG'] = 'C'
    os.environ['TZ'] = 'UTC'
    (options, args) = command_line_parser()
    count = int(options.count)
    interval = int(options.interval)
    count_str = "infinite" if count == -1 else str(count)
    status_msg = "Collecting system activity counters, %s iterations" % count_str
    status_msg += ", every %s second(s)" % options.interval
    max_time = int(options.max_time)
    print(status_msg)
    while count > 0 or count == -1:
        cmd = ["sar", "-pA", options.interval, "1"]
        if options.debug:
            print(cmd)
        rc, output, err = get_status_output(cmd)
        if rc != 0:
            print("Error invoking sar")
            print(err)
            sys.exit(1)
        parser = SarDataParser()
        for line in output.splitlines():
            line = line.strip("\r\n")
            parser.process(line)
        cmd = ["curl", "-km%d" % max_time,
               "-X", "POST", "-H", "Content-Type: application/json",
               "--data-binary", "@-", "%s/_doc/_bulk" % options.es_url]
        if options.debug:
            print(parser.json)
            print(cmd)
        rc, output, err = get_status_output(cmd, parser.json+"\n")
        if rc != 0:
            print(err)
            sys.exit(rc)
        if options.debug:
            print(output)
        if count != -1:
            count -= 1
        if count > 0 or count == -1:
            time.sleep(interval)


if __name__ == "__main__":
    main()
