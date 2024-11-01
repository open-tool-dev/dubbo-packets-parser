# parse dubbo packets using dpkt
parse dubbo packets and write the result into elasticsearch for analysis.

### Usage:

#### 1. create index in elasticsearch

create the index in the elasticsearch, the index definition is in assets/index.json

#### 2. capture the dubbo packets using tcpdump

use tcpdump tool to capture the dubbo packets, for example: tcpdump -vv port 20880 -w /tmp/dubbo-20880.pcap

#### 3. run the parse script to parse dubbo packets

python dubbo_parser.py --file #{dump_file} --port #{dubbo_port} --elastic_host #{es.host} --elastic_user #{es.user} --elastic_password #{es.password}

> --file #{dump_file}, required, the dubbo packets result file in step 2.

> --port #{dubbo_port}, required, dubbo server port, currently the script can not automatically recognize the dubbo port from the pcap result file.

> --elastic_host #{es.host}, optional, elasticsearch hosts

> --elastic_user #{es.user}, optional elasticsearch user

>  --elastic_password #{es.password}, optional, elasticsearch password

> --logfile #{logfile}, optional, the log path, default is /data/dubbo-parser-result.log.
