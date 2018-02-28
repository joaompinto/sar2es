#!/bin/sh
LANG=C
export S_TIME_FORMAT=ISO
while true; do sar -A 1 1|./sar2es.py  2>&1 |curl -sq -X POST -H "Content-Type: application/json" --data-binary @- http://localhost:9200/_doc/_bulk >/dev/null; sleep 1; done
