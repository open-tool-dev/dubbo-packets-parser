import argparse
from loguru import logger
from elasticsearch7 import Elasticsearch
from parser.dubbo_packet_parser import DubboPacketParser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="pcap file")
    parser.add_argument("--port", type=int, required=True, help="dubbo server port")
    parser.add_argument("--elastic_host", type=str, required=False, help="elasticsearch host", default="")
    parser.add_argument("--elastic_user", type=str, required=False, help="elasticsearch user", default="")
    parser.add_argument("--elastic_password", type=str, required=False, help="elasticsearch password", default="")
    parser.add_argument("--logfile", type=str, required=False, help="log file", default="/data/dubbo-parser-result.log")
    logger.remove(0)
    args = parser.parse_args()
    logger.add(args.logfile, rotation="1 hours", encoding="utf-8", backtrace=True,
               format="{time} | {level} | {message}")
    elastic_client = None
    if args.elastic_host:
        if args.elastic_user and args.elastic_password:
            elastic_client = Elasticsearch(
                hosts=[s.strip() for s in args.elastic_host.split(",")],
                http_auth=(args.elastic_user, args.elastic_password)
            )
        else:
            elastic_client = Elasticsearch(hosts=[s.strip() for s in args.elastic_host.split(",")])
    try:
        parser = DubboPacketParser(args.file, args.port, elastic_client)
        parser.parse()
    finally:
        parser.flush()
        if elastic_client:
            elastic_client.close()
