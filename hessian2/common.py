#!/bin/python
# -- coding: utf-8 --
import abc
import typing
from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class ObjectDefinition:
    type: str
    fields: list[str]


class AbstractHessian2Input(abc.ABC):

    @abstractmethod
    def add_ref(self, obj: typing.Any):
        pass

    @abstractmethod
    def read_end(self):
        pass

    @abstractmethod
    def is_end(self) -> bool:
        pass

    @abstractmethod
    def read_object(self):
        pass
