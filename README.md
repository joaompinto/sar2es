curl -XDELETE 'localhost:9200/sar?pretty'

curl -XPUT 'localhost:9200/sar?pretty' -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "_doc": {
      "dynamic_date_formats": ["dd-MM-yyyy HH:mm:ss"]
    }
  }
}'

