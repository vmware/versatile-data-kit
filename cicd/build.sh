#!/bin/bash
# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

echo "Starting build on $(uname -a)"

echo "Setup git hook scripts with pre-commit install"
pip install pre-commit
pre-commit install
