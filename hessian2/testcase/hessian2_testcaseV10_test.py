#!/bin/python
# -- coding: utf-8 --
import json

import hessian2.hessian2_input as hessian2_input
import base64
import subprocess
import time
from hessian2.testcase.hessian2_test import AbstractParserTest


class TestcaseMapParserTest(AbstractParserTest):
    """
    test class for map
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
                        "org.apache.dubbo.parser.parser.TestcaseV10MapParser",
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
                self.compare_dict(obj, testcase)
            finally:
                self.remove_files(file)
        testcase = [16, 256, 1024, 4096, 8192, 10240, 40960]
        for i in testcase:
            file = time.time_ns()
            try:
                process = subprocess.run(
                    [
                        "java", "-jar", f"{self.get_jar_path()}",
                        "org.apache.dubbo.parser.parser.TestcaseV10MapParser",
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
                print(f"testcase {i}")
                self.compare_dict(obj, testcase)
            finally:
                self.remove_files(file)