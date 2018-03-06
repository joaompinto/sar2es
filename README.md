
Opern a terminal window to download/install/start Elasticsearch:
```sh
cd ~/performance
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.2.tar.gz
tar xvf elasticsearch-6.2.2.tar.gz
elasticsearch-6.2.2/bin/elasticsearch
```

Open a terminal window to download/install/start Kibana
```sh
cd ~/performance
wget https://artifacts.elastic.co/downloads/kibana/kibana-6.2.2-linux-x86_64.tar.gz
tar xvf kibana-6.2.2-linux-x86_64.tar.gz
kibana-6.2.2-linux-x86_64/bin/kibana
```

Open a terminal window to download/run sar2es:
```bash
cd ~/performance
git clone https://github.com/joaompinto/sar2es.git
cd sar2es
./sar2es.py -c -1 -i 5
```

Open Kibana in a browser window at http://localhost:5601, setup the dashboard:

- Management -> Index Patterns -> In the "Index pattern" field, type: sar* -> Next step
- Select "@timestamp" for the Time Filter field name -> Create index pattern
- Management -> Saved Objects -> Import -> Select "kibana_sar_dashboard.json" -> Yes, overwrite
- Dashboard -> System Performance


