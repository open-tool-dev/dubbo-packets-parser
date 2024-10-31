from enum import Enum
from collections import deque
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


class ParserState(Enum):
    NONE = 0
    STATE_PARSE_HEADER = 1
    STATE_PARSE_BODY = 2


@dataclass_json
@dataclass
class CommonState:
    """
    dubbo request common state
    """
    state: ParserState = field(init=False, default=ParserState.STATE_PARSE_HEADER)
    is_event: bool = field(init=False, default=False)
    request_id: int = field(init=False, default=-1)
    request_len: int = field(init=False, default=0)
    status: int = field(init=False, default=0)


@dataclass_json
@dataclass
class ResponseState(CommonState):
    is_heartbeat: bool = field(init=False, default=False)


@dataclass_json
@dataclass
class RequestState(CommonState):
    """
    dubbo RequestState class.
    """
    is_two_way: bool = field(init=False, default=False)


@dataclass_json
@dataclass
class DubboResponse:
    """
    dubbo response class.
    """
    src_host: str
    src_port: int
    dest_host: str
    dest_port: int
    state: ResponseState = field(init=False, default=None)
    content: bytes = field(init=False, default=None)
    end_time: float = field(init=False, default=0)


@dataclass_json
@dataclass
class DubboRequest:
    """
    dubbo request class.
    """
    src_host: str
    src_port: int
    dest_host: str
    dest_port: int
    start_time: float = field(init=False, default=0)
    content: bytes = field(
        init=False, default=None
    )
    state: RequestState = field(
        init=False, default=None
    )


class PacketTime:

    def __init__(self, ts: float, size: int):
        self.ts = ts
        self.size = size


class DubboChannel:
    HEADER_LEN = 16

    MAGIC = [0xda, 0xbb]

    FLAG_REQUEST = 0x80

    FLAG_TWO_WAY = 0x40

    FLAG_EVENT = 0x20

    def __init__(self, src_host: str, src_port: int, dest_host: str, dest_port: int):
        self.src_host = src_host
        self.src_port = src_port
        self.dest_host = dest_host
        self.dest_port = dest_port
        self._request_packets = bytearray()
        self._request_packets_ts = deque[(float, int)]()
        self._response_packets = bytearray()
        self._response_packets_ts = deque[(float, int)]()
        self._current_request_state = RequestState()
        self._current_response_state = ResponseState()

    def append_and_try_parse_request(self, packet: bytes, ts: float) -> DubboRequest:
        self._append_request_packet(packet, ts)
        return self._try_parse_request()

    def append_and_try_parse_response(self, packet: bytes, ts: float) -> DubboResponse:
        self._append_response_packet(packet, ts)
        return self._try_parse_response()

    def _append_request_packet(self, packet: bytes, ts: float):
        self._request_packets.extend(packet)
        self._request_packets_ts.append(PacketTime(ts, len(packet)))

    def _append_response_packet(self, packet: bytes, ts: float):
        self._response_packets.extend(packet)
        self._response_packets_ts.append(PacketTime(ts, len(packet)))

    def _try_parse_request(self) -> DubboRequest | None:
        if self._current_request_state.state == ParserState.STATE_PARSE_HEADER:
            if len(self._request_packets) >= DubboChannel.HEADER_LEN:
                if not DubboChannel._is_match_magic(self._request_packets[0:2]):
                    raise Exception("dubbo network packet is illegal. magic mismatch 0xdabb.")
                type_byte = self._request_packets[2]
                if type_byte & DubboChannel.FLAG_REQUEST == 0:
                    raise Exception("packet is not dubbo request.")
                type_byte = type_byte & ~DubboChannel.FLAG_REQUEST
                self._current_request_state.is_two_way = (type_byte & DubboChannel.FLAG_TWO_WAY) != 0
                self._current_request_state.is_event = (type_byte & DubboChannel.FLAG_EVENT) != 0
                self._current_request_state.request_id = DubboChannel.get_request_id(self._request_packets[4:12])
                self._current_request_state.request_len = DubboChannel.get_request_len(self._request_packets[12:16])
                self._request_packets = self._request_packets[16:]
                self._current_request_state.state = ParserState.STATE_PARSE_BODY
        if self._current_request_state.state == ParserState.STATE_PARSE_BODY:
            if len(self._request_packets) >= self._current_request_state.request_len:
                request = DubboRequest(
                    src_host=self.src_host, src_port=self.src_port, dest_host=self.dest_host, dest_port=self.dest_port
                )
                request.content = self._request_packets[0:self._current_request_state.request_len]
                self._request_packets = self._request_packets[self._current_request_state.request_len:]
                self._current_request_state.state = ParserState.STATE_PARSE_HEADER
                request.state = self._current_request_state
                self._current_request_state = RequestState()
                first_ts = DubboChannel._remove_packet_from_queue(
                    self._request_packets_ts, self._current_request_state.request_len + DubboChannel.HEADER_LEN
                )
                request.start_time = first_ts
                return request
        return None

    def _try_parse_response(self) -> DubboResponse | None:
        if self._current_response_state.state == ParserState.STATE_PARSE_HEADER:
            if len(self._response_packets) >= DubboChannel.HEADER_LEN:
                if not DubboChannel._is_match_magic(self._response_packets[0:2]):
                    raise Exception("dubbo network packet is illegal. magic mismatch 0xdabb.")
                type_byte = self._response_packets[2]
                self._current_response_state.is_heartbeat = (type_byte & DubboChannel.FLAG_EVENT) != 0
                self._current_response_state.is_event = (type_byte & DubboChannel.FLAG_EVENT) != 0
                self._current_response_state.status = self._response_packets[3]
                self._current_response_state.request_id = DubboChannel.get_request_id(self._response_packets[4:12])
                self._current_response_state.request_len = DubboChannel.get_request_len(self._response_packets[12:16])
                self._response_packets = self._response_packets[DubboChannel.HEADER_LEN:]
                self._current_response_state.state = ParserState.STATE_PARSE_BODY
        if self._current_response_state.state == ParserState.STATE_PARSE_BODY:
            if len(self._response_packets) >= self._current_response_state.request_len:
                response = DubboResponse(self.src_host, self.src_port, self.dest_host, self.dest_port)
                response.content = self._response_packets[0:self._current_response_state.request_len]
                self._response_packets = self._response_packets[self._current_response_state.request_len:]
                self._current_response_state.state = ParserState.STATE_PARSE_HEADER
                response.state = self._current_response_state
                self._current_response_state = ResponseState()
                last_ts = DubboChannel._remove_packet_from_queue(
                    self._response_packets_ts, self._current_response_state.request_len + DubboChannel.HEADER_LEN, True
                )
                response.end_time = last_ts
                return response
        return None

    @staticmethod
    def _remove_packet_from_queue(queue: deque[PacketTime], size: int, last_packet: bool = False) -> float:
        left = size
        if len(queue) <= 0:
            raise Exception("parse packet error")
        ts = queue[0].ts
        while True:
            if len(queue) <= 0:
                raise Exception("parse packet error")
            item = queue[0]
            if last_packet:
                ts = item.ts
            if item.size > left:
                item.size = item.size - left
                break
            else:
                left = left - item.size
                queue.popleft()
                if left <= 0:
                    break
        return ts

    @staticmethod
    def _is_match_magic(buffer: bytes) -> bool:
        return buffer[0] == DubboChannel.MAGIC[0] and buffer[1] == DubboChannel.MAGIC[1]

    @staticmethod
    def get_request_id(buffer: bytes) -> int:
        return buffer[0] << 56 | buffer[1] << 48 | buffer[2] << 40 | buffer[3] << 32 \
            | buffer[4] << 24 | buffer[5] << 16 | buffer[6] << 8 | buffer[7]

    @staticmethod
    def get_request_len(buffer: bytes) -> int:
        return buffer[0] << 24 | buffer[1] << 16 | buffer[2] << 8 | buffer[3]
