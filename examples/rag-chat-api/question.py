# Copyright 2023-2025 Broadcom
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import sys

import requests


def get_api_response(question):
    headers = {"Content-Type": "application/json"}
    data = {"question": question}
    res = requests.post("http://127.0.0.1:8000/question/", headers=headers, json=data)

    return res.text.replace("\\n", "\n").replace("\\t", "\t")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrap your question in quotation marks")

    print(get_api_response(sys.argv[1]))
