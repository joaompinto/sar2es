
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
sh -v collect_local_stats.sh
```

Open Kibana in a browser window at http://localhost:5601

- Management -> Index Patterns -> Index pattern: sar* -> Next step
- Select "timestamp" for the Time Filter field name -> Create index pattern
- Discover -> Add a filter -> name is CPU -> Save
- Discover -> Add a filter -> component is all -> Save
- Visualize -> + Create a visualization -> Visual Builder
- Click "Panel options" -> Time field -> Selec timestamp
- Click "Data" -> change Aggregation to "Average" -> change filed to "metric.%usr"
- Click "Auto-refresh" -> 5seconds


