#!/bin/python
# -- coding: utf-8 --
import typing

from hessian2.common import AbstractHessian2Input


class ListDeserializer:

    def __init__(self, length: int):
        self.length = length

    def read_length_list(self, input_stream: AbstractHessian2Input) -> typing.List:
        result_list = []
        if self.length >= 0:
            for i in range(0, self.length):
                result_list.append(input_stream.read_object())
        else:
            while not input_stream.is_end():
                result_list.append(input_stream.read_object())
            input_stream.read_end()
        return result_list


class MapDeserializer:

    def __init__(self, key_type: str = None, value_type: str = None):
        self.key_type = key_type
        self.value_type = value_type

    def read_map(self, input_stream: AbstractHessian2Input):
        result = {}
        while not input_stream.is_end():
            key = input_stream.read_object()
            value = input_stream.read_object()
            result[key] = value
        input_stream.read_end()
        return result


class ObjectDeserializer:

    def __init__(self, field_names: list[str]):
        self.field_names = field_names

    def read_object(self, input_stream: AbstractHessian2Input):
        result = {}
        for field_name in self.field_names:
            result[field_name] = input_stream.read_object()
        return result
