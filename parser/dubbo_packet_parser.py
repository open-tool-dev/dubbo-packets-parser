import json

import dpkt
import socket
from parser.dubbo_common import (DubboChannel, DubboRequest, DubboResponse)
from loguru import logger
import time
from hessian2.hessian2_input import Hessian2Input
from elasticsearch7 import Elasticsearch

RESPONSE_VALUE = 1
RESPONSE_WITH_EXCEPTION_WITH_ATTACHMENTS = 3
RESPONSE_WITH_EXCEPTION = 0
RESPONSE_NULL_VALUE_WITH_ATTACHMENTS = 5
RESPONSE_VALUE_WITH_ATTACHMENTS = 4

OK = 20


class DubboPacketParser:
    """
    dubbo packets parser class.
    """

    def __init__(self, file: str, port: int, elastic_client: Elasticsearch):
        self.file = file
        self.port = port
        self._channels = dict[str, DubboChannel]()
        self._requests = dict[str, dict[int, DubboRequest]]()
        self._elastic_client = elastic_client
        self._batch_queue = []
        self._index_name = "dubbo_packets"

    def parse(self):
        with open(self.file, mode="rb") as f:
            pcap = dpkt.pcap.Reader(f)
            try:
                for ts, pkt in pcap:
                    eth = dpkt.ethernet.Ethernet(pkt)
                    ip = eth.data
                    tcp = ip.data
                    src_ip = socket.inet_ntoa(ip.src)
                    dst_ip = socket.inet_ntoa(ip.dst)
                    src_port = tcp.sport
                    dst_port = tcp.dport
                    if dst_port == self.port:
                        key = f"{src_ip}:{src_port}->{dst_ip}:{dst_port}"
                        if key not in self._channels:
                            self._channels[key] = DubboChannel(src_ip, src_port, dst_ip, dst_port)
                        if len(tcp.data) > 0:
                            request = self._channels[key].append_and_try_parse_request(tcp.data, ts)
                            if request:
                                if key not in self._requests:
                                    self._requests[key] = dict[int, DubboRequest]()
                                self._requests[key][request.state.request_id] = request
                    else:
                        key = f"{dst_ip}:{dst_port}->{src_ip}:{src_port}"
                        if key not in self._channels:
                            self._channels[key] = DubboChannel(dst_ip, dst_port, src_ip, src_port)
                        if len(tcp.data) > 0:
                            response = self._channels[key].append_and_try_parse_response(tcp.data, ts)
                            if response:
                                try:
                                    if response.state.request_id in self._requests[key]:
                                        request = self._requests[key][response.state.request_id]
                                        self.on_dubbo_call_parsed(
                                            dst_ip, dst_port, src_ip, src_port, request, response
                                        )
                                    else:
                                        logger.warning(f"not found request {response.state.request_id}")
                                finally:
                                    del self._requests[key][response.state.request_id]
                    if (tcp.flags & dpkt.tcp.TH_RST) != 0 or (tcp.flags & dpkt.tcp.TH_FIN) != 0:
                        if key in self._requests:
                            for k, v in self._requests[key].items():
                                if dst_port == self.port:
                                    self.on_dubbo_call_parsed(src_ip, src_port, dst_ip, dst_port, v)
                                else:
                                    self.on_dubbo_call_parsed(dst_ip, dst_port, src_ip, src_port, v)
                            del self._requests[key]
            except Exception as e:
                raise e
        print("******* parse dubbo packets success *******")

    def on_dubbo_call_parsed(self, src_ip, src_port, dest_ip, dest_port, request: DubboRequest,
                             response: DubboResponse = None):
        if request:
            start_time = request.start_time
            end_time = response.end_time if response is not None else time.time()
            cost_time = end_time - start_time
            if request and request.state and not request.state.is_event:
                document = {
                    "@timestamp": int(request.start_time * 1000),
                    "start_time": request.start_time,
                    "end_time": end_time,
                    "src_addr": src_ip,
                    "src_port": src_port,
                    "dst_addr": dest_ip,
                    "dst_port": dest_port,
                    "cost_time_ms": cost_time * 1000
                }
                hessianInput = Hessian2Input(request.content)
                hessianInput.read_utf()
                service_name = hessianInput.read_utf()
                service_version = hessianInput.read_utf()
                method_name = hessianInput.read_utf()
                desc = hessianInput.read_utf()
                parameters = []
                if len(desc) > 0:
                    parts = [p for p in desc.split(";") if len(p) > 0]
                    for _ in range(0, len(parts)):
                        param = hessianInput.read_object()
                        parameters.append(param)
                attachments = hessianInput.read_object()
                document.update(
                    {
                        "service_name": service_name,
                        "service_version": service_version,
                        "method_name": method_name,
                        "parameters": json.dumps(parameters, ensure_ascii=False),
                        "request_attachments": json.dumps(attachments, ensure_ascii=False),
                    }
                )
                if response:
                    hessianInput = Hessian2Input(response.content)
                    if response.state.status == OK:
                        if not response.state.is_heartbeat:
                            b = hessianInput.read_int()
                            if b == RESPONSE_VALUE_WITH_ATTACHMENTS or b == RESPONSE_VALUE:
                                result = hessianInput.read_object()
                                if result:
                                    document["result"] = json.dumps(result)
                                elif b == RESPONSE_WITH_EXCEPTION_WITH_ATTACHMENTS or b == RESPONSE_WITH_EXCEPTION:
                                    error = hessianInput.read_object()
                                    if error:
                                        document["error"] = json.dumps(error)
                                if b == RESPONSE_NULL_VALUE_WITH_ATTACHMENTS or b == RESPONSE_VALUE_WITH_ATTACHMENTS \
                                        or b == RESPONSE_WITH_EXCEPTION_WITH_ATTACHMENTS:
                                    res_attach = hessianInput.read_object()
                                    document["response_attachments"] = json.dumps(res_attach)
                    else:
                        document["error"] = hessianInput.read_utf()
                if len(document) > 0:
                    self._try_append_flush(document)

    def _try_append_flush(self, document: dict):
        if not self._elastic_client:
            return
        self._batch_queue.append(document)
        if len(self._batch_queue) > 128:
            self.flush()

    def flush(self):
        if not self._elastic_client:
            return
        actions = []
        for doc in self._batch_queue:
            actions.append({"index": {"_index": self._index_name}})
            actions.append(json.dumps(doc))
        self._elastic_client.bulk(body=actions, index=self._index_name)
        self._batch_queue.clear()
