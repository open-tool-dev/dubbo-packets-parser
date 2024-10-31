#!/bin/python
# -- coding: utf-8 --
import json

import hessian2.hessian2_input as hessian2_input
import base64
import subprocess
import time
from hessian2.testcase.hessian2_test import AbstractParserTest


class TestcaseListParserTest(AbstractParserTest):
    """
    test class for list
    """

    def test(self):
        testcase = [16, 256, 1024, 4096, 8192, 10240, 40960]
        for i in testcase:
            file = time.time_ns()
            try:
                print(f"testcase {i}")
                process = subprocess.run(
                    [
                        "java", "-jar", f"{self.get_jar_path()}",
                        "org.apache.dubbo.parser.parser.TestcaseV2ListParser",
                        "--count", "16", "--size", f"{i}", "--outfile", f"/tmp/{file}"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                errors = process.stderr
                if process.returncode != 0:
                    print(errors)
                    raise Exception("run encode method failed")
                with open(file=f"/tmp/{file}.txt", mode="r") as f:
                    content = f.read()
                b = base64.b64decode(content)
                decoder = hessian2_input.Hessian2Input(b)
                obj = decoder.read_object()
                with open(file=f"/tmp/{file}.json", mode="r") as f:
                    content = f.read()
                testcase = json.loads(content)
                assert len(obj) == len(testcase)
                for k in range(0, len(testcase)):
                    p, n = obj[k], testcase[k]
                    props = ["field0", "field1"]
                    for prop in props:
                        assert p[prop] == n[prop]
            finally:
                self.remove_files(file)
        testcase = [16, 256, 1024, 4096, 8192, 10240, 40960]
        for i in testcase:
            file = time.time_ns()
            try:
                process = subprocess.run(
                    [
                        "java", "-jar", f"{self.get_jar_path()}",
                        "org.apache.dubbo.parser.parser.TestcaseV2ListParser",
                        "--count", f"{i}", "--size", "256", "--outfile", f"/tmp/{file}"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                errors = process.stderr
                if process.returncode != 0:
                    print(errors)
                    raise Exception("run encode method failed")
                with open(file=f"/tmp/{file}.txt", mode="r") as f:
                    content = f.read()
                b = base64.b64decode(content)
                decoder = hessian2_input.Hessian2Input(b)
                obj = decoder.read_object()
                with open(file=f"/tmp/{file}.json", mode="r") as f:
                    content = f.read()
                testcase = json.loads(content)
                assert len(obj) == len(testcase)
                for k in range(0, len(testcase)):
                    p, n = obj[k], testcase[k]
                    props = ["field0", "field1"]
                    for prop in props:
                        assert p[prop] == n[prop]
            finally:
                self.remove_files(file)
