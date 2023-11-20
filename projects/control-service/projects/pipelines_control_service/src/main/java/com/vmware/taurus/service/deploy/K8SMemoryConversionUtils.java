/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

public class K8SMemoryConversionUtils {

  public static int getMemoryInMi(String memory, int amount) {
    if (memory.endsWith("K")) {
      return amount / 1000;
    }
    if (memory.endsWith("Ki")) {
      return amount / 1024;
    }
    if (memory.endsWith("Gi")) {
      return amount * 1024;
    }
    if (memory.endsWith("G")) {
      return amount * 1000;
    }
    if (memory.endsWith("T")) {
      return amount * 1000000;
    }
    if (memory.endsWith("Ti")) {
      return amount * 1048576;
    }
    return amount;
  }
}
