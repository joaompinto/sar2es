#!/bin/sh
while true; do sar -A 1 1|./sar2el.py  2>&1 |curl -X POST -H "Content-Type: application/json" --data-binary @- http://localhost:9200/_doc/_bulk; sleep 1; done
