# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys

import requests


def question():
    if len(sys.argv) != 2:
        print("Wrap your question in quotation marks")

    headers = {"Content-Type": "application/json"}
    data = {"question": sys.argv[1]}
    res = requests.post("http://127.0.0.1:8000/question/", headers=headers, json=data)

    print(res.text.replace("\\n", "\n").replace("\\t", "\t"))


if __name__ == "__main__":
    question()
