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
from __future__ import print_function
from datetime import datetime
from pprint import pprint
from os import environ
import sys
import re
import fileinput
import json


class SarDataParser:

    def __init__(self):
        self.metrics_info = None
        self.metrics_header = None
        self.metrics_data = []
        self.all_data = []

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
                # Ignore this types of data
                if self.metrics_header[1] in ["BUS", "FAN", "TEMP"]:
                    return
                for metric_record in self.metrics_data:
                    timestamp_str = self.metrics_info[0][3]+" "+metric_record[0]
                    #timestamp = datetime.strptime(timestamp_str, "%d-%m-%Y %H:%M:%S")
                    #timestamp_int = long(timestamp.strftime('%s'))
                    metrics = {}
                    for i in range(base_index, len(self.metrics_header)):
                        metrics[self.metrics_header[i]] = float(metric_record[i].replace(',', '.'))
                    json_record = {
                        'hostname': self.metrics_info[0][2],
                        'date': timestamp_str,
                        'name': metric_name,
                        'component' : metric_record[1],
                        'metrics': metrics
                    }
                    print('{ "index":  { "_index": "sar", "_type": "_doc" }}')
                    print(json.dumps(json_record, ensure_ascii=False, sort_keys=True))
            self.metrics_header = None
            self.metrics_data = []
        elif self.metrics_info is None:
            self.metrics_info = re.findall(r"(\S+)\s+(\S+)\s+\(([\w\.]+)\)\s+(\S+)", line)
        elif self.metrics_header is None:
            self.metrics_header = line.split()
        else:
            self.metrics_data.append(line.split())

    def pprint_result(self):
        pprint(self.data_dict)


def main():
    environ['LANG'] = 'C'
    parser = SarDataParser()
    for line in fileinput.input():
        line = line.strip("\r\n")
        parser.process(line)
    print("")   # EOF for ES bulk processing

if __name__ == "__main__":
    main()
