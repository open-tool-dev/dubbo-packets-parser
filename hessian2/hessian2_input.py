#!/bin/python
# -- coding: utf-8 --
import datetime
import struct
import typing
from ctypes import c_int32, c_int64, c_double
from io import StringIO

from hessian2.common import ObjectDefinition, AbstractHessian2Input
from hessian2.serializers import ObjectDeserializer, ListDeserializer, MapDeserializer

BC_INT_ZERO = 0x90
BC_INT_BYTE_ZERO = 0xc8
BC_INT_SHORT_ZERO = 0xd4
BC_LONG_INT = 0x59
BC_LONG_ZERO = 0xe0
BC_LONG_BYTE_ZERO = 0xf8
BC_LONG_SHORT_ZERO = 0x3c
BC_DOUBLE_ZERO = 0x5b
BC_DOUBLE_ONE = 0x5c
BC_DOUBLE_BYTE = 0x5d
BC_DOUBLE_SHORT = 0x5e
BC_DOUBLE_MILL = 0x5f
BC_STRING_CHUNK = 'R'
BC_DATE = 0x4a
BC_DATE_MINUTE = 0x4b
BC_BINARY_CHUNK = 'A'
BC_LIST_VARIABLE = 0x55
BC_LIST_VARIABLE_UNTYPED = 0x57
BC_LIST_FIXED = 'V'
BC_LIST_FIXED_UNTYPED = 0x58
BC_REF = 0x51


class Hessian2Input(AbstractHessian2Input):
    """
    hessian decoder
    """

    def __init__(self, buffer: bytes):
        self._buffer = buffer
        self._offset = 0
        self._length = len(self._buffer)
        self._chunk_length = 0
        self._is_last_chunk = False
        self._types = list[str]()
        self._refs = list[typing.Any]()
        self._class_def_list = list[ObjectDefinition]()

    def read_object(self) -> typing.Any:
        tag = self.read_byte()
        match tag:
            case tag if tag == ord('N'):
                return None
            case tag if tag == ord('T'):
                return True
            case tag if tag == ord('F'):
                return False
            case tag if 0x80 <= tag <= 0xbf:
                return int(tag - BC_INT_ZERO)
            case tag if 0xc0 <= tag <= 0xcf:
                return int(((tag - BC_INT_BYTE_ZERO) << 8) + self._read_byte())
            case tag if 0xd0 <= tag <= 0xd7:
                return int(((tag - BC_INT_SHORT_ZERO) << 16) + (self._read_byte() << 8) + self._read_byte())
            case tag if tag == ord('I'):
                return int(self.parse_int())
            case tag if 0xd8 <= tag <= 0xef:
                return int(tag - BC_LONG_ZERO)
            case tag if 0xf0 <= tag <= 0xff:
                return int(((tag - BC_LONG_BYTE_ZERO) << 8) + self._read_byte())
            case tag if 0x38 <= tag <= 0x3f:
                return int(((tag - BC_LONG_SHORT_ZERO) << 16) + (self._read_byte() << 8) + self._read_byte())
            case tag if tag == BC_LONG_INT:
                return int(self.parse_int())
            case tag if tag == ord('L'):
                return int(self.parse_long())
            # double parser
            case tag if tag == BC_DOUBLE_ZERO:
                return c_double(0).value
            case tag if tag == BC_DOUBLE_ONE:
                return c_double(1).value
            case tag if tag == BC_DOUBLE_BYTE:
                return c_double(self._read_byte()).value
            case tag if tag == BC_DOUBLE_SHORT:
                return c_double((self._read_byte() << 8) + self._read_byte()).value
            case tag if tag == BC_DOUBLE_MILL:
                mills = self.parse_int()
                return c_double(0.001 * mills).value
            case tag if tag == ord('D'):
                return c_double(self.parse_double()).value
            case tag if tag == BC_DATE:
                val = self.parse_long()
                return datetime.datetime.fromtimestamp(val / 1000)
            #
            case tag if tag == BC_DATE_MINUTE:
                return datetime.datetime.fromtimestamp(self.parse_int() * 60000)
            case tag if tag == ord(BC_STRING_CHUNK) or tag == ord('S'):
                self._is_last_chunk = (tag == ord('S'))
                self._chunk_length = (self._read_byte() << 8) + self._read_byte()
                return self.parse_string()
            case tag if 0x00 <= tag <= 0x1f:
                self._is_last_chunk = True
                self._chunk_length = int(tag - 0x00)
                return self.parse_string()
            case tag if 0x30 <= tag <= 0x33:
                self._is_last_chunk = True
                self._chunk_length = ((tag - 0x30) << 8) + self._read_byte()
                return self.parse_string()
            case tag if tag == ord(BC_BINARY_CHUNK) or tag == ord('B'):
                self._is_last_chunk = (tag == ord('B'))
                self._chunk_length = (self._read_byte() << 8) + self._read_byte()
                buffer = bytearray()
                while True:
                    b = self.parse_byte()
                    if b is not None:
                        buffer.append(b.to_bytes(1, "big")[0:1])
                    else:
                        break
                return buffer[0:]
            case tag if 0x20 <= tag <= 0x2f:
                self._is_last_chunk = True
                lens = tag - 0x20
                self._chunk_length = 0
                buffer = bytearray()
                while lens >= 0:
                    b = self._read_byte()
                    buffer.append(b.to_bytes(1, 'big')[0:1])
                    lens = lens - 1
                return buffer[0:]
            case tag if 0x34 <= tag <= 0x37:
                self._is_last_chunk = True
                lens = ((tag - 0x34) << 8) + self._read_byte()
                self._chunk_length = 0
                buffer = bytearray()
                while lens >= 0:
                    b = self._read_byte()
                    buffer.append(b.to_bytes(1, 'big')[0:1])
                    lens = lens - 1
                return buffer[0:]
            case tag if tag == BC_LIST_VARIABLE:
                self.read_type()
                return ListDeserializer(-1).read_length_list(self)
            case tag if tag == BC_LIST_VARIABLE_UNTYPED:
                return ListDeserializer(-1).read_length_list(self)
            case tag if tag == ord(BC_LIST_FIXED):
                self.read_type()
                lens = self.read_int()
                return ListDeserializer(lens).read_length_list(self)
            case tag if tag == BC_LIST_FIXED_UNTYPED:
                lens = self.read_int()
                return ListDeserializer(lens).read_length_list(self)
            case tag if 0x70 <= tag <= 0x77:
                self.read_type()
                lens = tag - 0x70
                return ListDeserializer(lens).read_length_list(self)
            case tag if 0x78 <= tag <= 0x7f:
                lens = tag - 0x78
                return ListDeserializer(lens).read_length_list(self)
            case tag if tag == ord('H'):
                return MapDeserializer().read_map(self)
            case tag if tag == ord('M'):
                self.read_type()
                map_result = MapDeserializer().read_map(self)
                self.add_ref(map_result)
                return map_result
            case tag if tag == ord('C'):
                self.read_object_definition()
                obj = self.read_object()
                return obj
            case tag if 0x60 <= tag <= 0x6f:
                ref = tag - 0x60
                if ref >= len(self._class_def_list):
                    raise Exception(f"No classes defined at reference {ref}")
                class_def = self._class_def_list[ref]
                value = ObjectDeserializer(class_def.fields).read_object(self)
                self.add_ref(value)
                return value
            case tag if tag == ord('O'):
                ref = self.read_int()
                class_def = self._class_def_list[ref]
                value = ObjectDeserializer(class_def.fields).read_object(self)
                self.add_ref(value)
                return value
            case tag if tag == BC_REF:
                # TODO
                ref = self.read_int()
                return None
                # do not support ref
                # return self._refs[ref]
            case _:
                if tag is None:
                    raise Exception("readObject: unexpected end of file")
                else:
                    raise Exception(f"readObject: unknown code {tag}")

    def read_object_definition(self):
        tp = self.read_string()
        lens = self.read_int()
        field_names = []
        for i in range(0, lens):
            field_names.append(self.read_string())
        class_def = ObjectDefinition(type=tp, fields=field_names)
        self._class_def_list.append(class_def)

    def read_int(self):
        tag = self._read_byte()
        match tag:
            case tag if tag == ord('N'):
                return 0
            case tag if tag == ord('F'):
                return 0
            case tag if tag == ord('T'):
                return 1
            case tag if 0x80 <= tag <= 0xbf:
                return int(tag - BC_INT_ZERO)
            case tag if 0xc0 <= tag <= 0xcf:
                return ((tag - BC_INT_BYTE_ZERO) << 8) + self._read_byte()
            case tag if 0xd0 <= tag <= 0xd7:
                return ((tag - BC_INT_SHORT_ZERO) << 16) + 256 * self._read_byte() + self._read_byte()
            case tag if tag == ord('I') or tag == BC_LONG_INT:
                return (self._read_byte() << 24) + (self._read_byte() << 16) + (self._read_byte() << 8) \
                    + self._read_byte()
            case tag if 0xd8 <= tag <= 0xef:
                return tag - BC_LONG_ZERO
            case tag if 0xf0 <= tag <= 0xff:
                return ((tag - BC_LONG_BYTE_ZERO) << 8) + self._read_byte()
            case tag if 0x38 <= tag <= 0x3f:
                return ((tag - BC_LONG_SHORT_ZERO) << 16) + 256 * self._read_byte() + self._read_byte()
            case tag if tag == ord('L'):
                return self.parse_long()
            case tag if tag == BC_DOUBLE_ZERO:
                return 0
            case tag if tag == BC_DOUBLE_ONE:
                return 1
            case tag if tag == BC_DOUBLE_BYTE:
                return self._read_byte()
            case tag if tag == BC_DOUBLE_SHORT:
                return self._read_byte() << 8 + self._read_byte()
            case tag if tag == BC_DOUBLE_MILL:
                mills = self.parse_int()
                return int(0.001 * mills)
            case tag if tag == ord('D'):
                return int(self.parse_double())
            case _:
                raise Exception(f"expect integer")

    def read_type(self):
        code = self._read_byte()
        self._offset = self._offset - 1
        match code:
            case code if 0x00 <= code <= 0x1f or 0x30 <= code <= 0x33 \
                         or code == ord(BC_STRING_CHUNK) or code == ord('S'):
                tp = self.read_string()
                self._types.append(tp)
                return tp
            case _:
                ref = self.read_int()
                if len(self._types) <= ref:
                    raise Exception(f"type ref {ref} is greater than the number of valid types({len(self._types)})")
                return self._types[ref]

    def parse_byte(self):
        while self._chunk_length <= 0:
            if self._is_last_chunk:
                return -1
            code = self._read_byte()
            match code:
                case code if code == ord(BC_BINARY_CHUNK):
                    self._is_last_chunk = False
                    self._chunk_length = (self._read_byte() << 8) + self._read_byte()
                case code if code == ord('B'):
                    self._is_last_chunk = True
                    self._chunk_length = (self._read_byte() << 8) + self._read_byte()
                case code if 0x20 <= code <= 0x2f:
                    self._is_last_chunk = True
                    self._chunk_length = code - 0x20
                case code if 0x34 <= code <= 0x37:
                    self._is_last_chunk = True
                    self._chunk_length = (code - 0x34) * 256 + self._read_byte()
                case _:
                    raise Exception(f"expect byte[], got {code}")
        self._chunk_length = self._chunk_length - 1
        return self.read_byte()

    def parse_string(self):
        str_out = StringIO()
        while True:
            if self._chunk_length <= 0:
                if not self.parse_chunk_length():
                    break
            length = self._chunk_length
            self._chunk_length = 0
            while length > 0:
                str_out.write(chr(self.parse_utf8_char()))
                length = length - 1
        return str_out.getvalue()

    def read_utf(self) -> str:
        return self.read_string()

    def read_string(self):
        tag = self.read_byte()
        if tag is None:
            return None
        match tag:
            case tag if tag == ord('N'):
                return None
            case tag if tag == ord('T'):
                return "true"
            case tag if tag == ord('F'):
                return "false"
            case tag if 0x80 <= tag <= 0xbf:
                return str(tag - 0x90)
            case tag if 0xc0 <= tag <= 0xcf:
                result = ((tag - BC_INT_BYTE_ZERO) << 8) + self._read_byte()
                return str(result)
            case tag if 0xd0 < tag <= 0xd7:
                result = ((tag - BC_INT_SHORT_ZERO) << 16) + (self._read_byte() << 8) + self._read_byte()
                return str(result)
            case tag if tag == ord('I') or tag == BC_LONG_INT:
                return str(self.parse_int())
            case tag if 0xd8 <= tag <= 0xdf or 0xe0 <= tag <= 0xef:
                result = tag - BC_LONG_ZERO
                return str(result)
            case tag if 0xf0 <= tag <= 0xff:
                result = ((tag - BC_LONG_BYTE_ZERO) << 8) + self._read_byte()
                return str(result)
            case tag if 0x38 <= tag <= 0x3f:
                result = ((tag - BC_LONG_SHORT_ZERO) << 16) + (self._read_byte() << 8) + self._read_byte()
                return str(result)
            case tag if tag == ord('L'):
                return str(self.parse_long())
            case tag if tag == BC_DOUBLE_ZERO:
                return "0.0"
            case tag if tag == BC_DOUBLE_ONE:
                return "1.0"
            case tag if tag == BC_DOUBLE_BYTE:
                return str(self._read_byte())
            case tag if tag == BC_DOUBLE_SHORT:
                result = (self._read_byte() << 8) + self._read_byte()
                return str(result)
            case tag if tag == BC_DOUBLE_MILL:
                mills = self.parse_int()
                return str(0.001 * mills)
            case tag if tag == ord('D'):
                return str(self.parse_double())
            case tag if tag == ord('S') or tag == ord(BC_STRING_CHUNK):
                self._is_last_chunk = (tag == ord('S'))
                self._chunk_length = self._read_byte() << 8 + self._read_byte()
                str_output = StringIO()
                loop = True
                while loop:
                    ch = self.parse_char()
                    if ch < 0:
                        loop = False
                    else:
                        str_output.write(chr(ch))
                return str_output.getvalue()
            case tag if 0x00 <= tag <= 0x1f:
                self._is_last_chunk = True
                self._chunk_length = tag - 0x00
                str_output = StringIO()
                loop = True
                while loop:
                    ch = self.parse_char()
                    if ch < 0:
                        loop = False
                    else:
                        str_output.write(chr(ch))
                return str_output.getvalue()
            case tag if 0x30 <= tag <= 0x33:
                self._is_last_chunk = True
                self._chunk_length = ((tag - 0x30) << 8) + self._read_byte()
                loop = True
                str_output = StringIO()
                while loop:
                    ch = self.parse_char()
                    if ch < 0:
                        loop = False
                    else:
                        str_output.write(chr(ch))
                return str_output.getvalue()
            case _:
                raise Exception(f"expect {tag}")

    def parse_double(self):
        i64 = self.parse_long()
        return struct.unpack('d', struct.pack('Q', i64))[0]

    def parse_int(self):
        b32 = self._read_byte()
        b24 = self._read_byte()
        b16 = self._read_byte()
        b8 = self._read_byte()
        return c_int32((b32 << 24) + (b24 << 16) + (b16 << 8) + b8).value

    def parse_long(self):
        b64 = self._read_byte()
        b56 = self._read_byte()
        b48 = self._read_byte()
        b40 = self._read_byte()
        b32 = self._read_byte()
        b24 = self._read_byte()
        b16 = self._read_byte()
        b8 = self._read_byte()
        return c_int64(
            (b64 << 56) + (b56 << 48) + (b48 << 40) + (b40 << 32) + (b32 << 24) + (b24 << 16) + (b16 << 8) + b8
        ).value

    def parse_char(self):
        while self._chunk_length <= 0:
            if not self.parse_chunk_length():
                return -1
        self._chunk_length = self._chunk_length - 1
        return self.parse_utf8_char()

    def parse_utf8_char(self):
        ch = self._read_byte()
        if ch < 0x80:
            return ch
        elif (ch & 0xe0) == 0xc0:
            ch1 = self._read_byte()
            return ((ch & 0x1f) << 6) + (ch1 & 0x3f)
        elif (ch & 0xf0) == 0xe0:
            ch1 = self._read_byte()
            ch2 = self._read_byte()
            return ((ch & 0x0f) << 12) + ((ch1 & 0x3f) << 6) + (ch2 & 0x3f)
        else:
            raise Exception(f"bad utf-8 encoding at {ch}")

    def _read_byte(self):
        if self._offset < self._length:
            b = self._buffer[self._offset]
            self._offset = self._offset + 1
            return b
        else:
            raise Exception(f"exceed _buffer length, _offset={self._offset}, length={self._length}")

    def parse_chunk_length(self) -> bool:
        if self._is_last_chunk:
            return False
        code = self._buffer[self._offset]
        self._offset = self._offset + 1
        match code:
            case code if code == ord(BC_STRING_CHUNK):
                self._is_last_chunk = False
                high_byte = self._buffer[self._offset]
                self._offset = self._offset + 1
                low_byte = self._buffer[self._offset]
                self._offset = self._offset + 1
                self._chunk_length = (high_byte << 8) + low_byte
            case code if code == ord('S'):
                self._is_last_chunk = True
                high_byte = self._buffer[self._offset]
                self._offset = self._offset + 1
                low_byte = self._buffer[self._offset]
                self._offset = self._offset + 1
                self._chunk_length = (high_byte << 8) + low_byte
            case code if 0x00 <= code <= 0x1f:
                self._is_last_chunk = True
                self._chunk_length = code - 0x00
            case code if 0x30 <= code <= 0x33:
                self._is_last_chunk = True
                self._chunk_length = ((code - 0x30) << 8) + self._buffer[self._offset]
                self._offset = self._offset + 1
            case _:
                raise Exception(f"expect string code {code}")
        return True

    def read_byte(self) -> int | None:
        if self._offset >= self._length:
            return None
        return self._read_byte() & 0xFF

    def read_end(self):
        code = self._read_byte()
        if code == ord('Z'):
            return
        elif code < 0:
            raise Exception("unexpected end of file")
        else:
            raise Exception(f"unknown code: {code}")

    def is_end(self) -> bool:
        if self._offset >= self._length:
            return True
        code = self._buffer[self._offset] & 0xFF
        return code == ord('Z')

    def add_ref(self, obj: typing.Any):
        self._refs.append(obj)
