/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.text.NumberFormat;
import java.text.ParseException;

public class K8SMemoryConversionUtils {

  public static int getMemoryInMi(int amount, String memory) {
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

  public static int getMemoryInMi(String memory) throws ParseException {
    var memoryAmount = NumberFormat.getInstance().parse(memory).intValue();
    return getMemoryInMi(memoryAmount, memory);
  }

  public static float getCpuInFloat(String cpu) throws ParseException {
    return NumberFormat.getInstance().parse(cpu).floatValue();
  }
}
