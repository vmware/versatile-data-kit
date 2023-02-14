#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

set_patch_version(){
  patch_version=$1
  current_version="$(python3 setup.py --version)"
  major_minor_version="${current_version%.*}"
  new_version="$major_minor_version.$patch_version"

  sed -i.bak "s/$current_version/$new_version/g" version.txt
}

set_patch_version "$1"
