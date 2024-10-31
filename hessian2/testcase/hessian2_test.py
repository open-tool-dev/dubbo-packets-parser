#!/bin/python
# -- coding: utf-8 --
import abc
import datetime
import os


class AbstractParserTest(abc.ABC):
    """
    abstract class for hessian parser.
    """

    @staticmethod
    def remove_files(file_name: str | int):
        if os.path.exists(f"/tmp/{file_name}.json"):
            os.remove(f"/tmp/{file_name}.json")
        if os.path.exists(f"/tmp/{file_name}.txt"):
            os.remove(f"/tmp/{file_name}.txt")

    @staticmethod
    def get_jar_path() -> str:
        val = os.environ.get("ENCODER_JAR")
        if val is not None:
            return val
        else:
            return "/data/dubbo-packet-testcase.jar"

    @staticmethod
    def compare_double(left: float, right: float, epsilon=1e-9):
        return abs(left - right) <= epsilon

    @staticmethod
    def compare_date(left, right):
        left_i64 = left
        if type(left) is datetime.datetime:
            left_i64 = left.timestamp() * 1000
        right_i64 = right
        if type(right) is datetime.datetime:
            right_i64 = right.timestamp() * 1000
        assert left_i64 == right_i64

    @staticmethod
    def compare_dict(left: dict, right: dict):
        assert len(left) == len(right)
        for lk, lv in left.items():
            if lk not in right:
                if type(lk) is datetime.datetime:
                    lk = lk.timestamp() * 1000
                lk = str(lk)
                right_value = right[lk]
            else:
                right_value = right[lk]
            left_value = lv
            if type(left_value) is datetime.datetime:
                left_value = str(left_value)
            if type(right_value) is datetime.datetime:
                right_value = str(right_value)
            if type(lv) is dict and type(right_value) is dict:
                AbstractParserTest.compare_dict(left_value, right_value)
            elif type(lv) is float and type(right_value) is float:
                AbstractParserTest.compare_double(left_value, right_value)
            elif type(lv) is datetime.datetime or right_value is datetime.datetime:
                AbstractParserTest.compare_date(left_value, right_value)
            else:
                assert left_value == right_value

