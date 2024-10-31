import argparse
from loguru import logger
import dubbo_packet_parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="pcap file")
    parser.add_argument("--port", type=int, required=True, help="dubbo server port")
    parser.add_argument("--result", type=str, required=True, help="dubbo result file")
    parser.add_argument(
        "--logfile", type=str, required=False, help="log file", default="dubbo-parser-result.log"
    )
    logger.remove(0)
    args = parser.parse_args()
    logger.add(args.logfile, rotation="1 hours", encoding="utf-8", backtrace=True,
               format="{time} | {level} | {message}")
    parser = dubbo_packet_parser.DubboPacketParser(args.file, args.port, args.result)
    parser.parse()
