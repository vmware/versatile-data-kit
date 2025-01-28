/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import java.text.NumberFormat;
import java.text.ParseException;

public class K8SMemoryConversionUtils {

  public static int getMemoryInMi(int amount, String memoryUnit) {
    if (memoryUnit.endsWith("K")) {
      return amount / 1000;
    }
    if (memoryUnit.endsWith("Ki")) {
      return amount / 1024;
    }
    if (memoryUnit.endsWith("Gi")) {
      return amount * 1024;
    }
    if (memoryUnit.endsWith("G")) {
      return amount * 1000;
    }
    if (memoryUnit.endsWith("T")) {
      return amount * 1000000;
    }
    if (memoryUnit.endsWith("Ti")) {
      return amount * 1048576;
    }
    return amount;
  }

  public static int getMemoryInMi(String memory) throws ParseException {
    var memoryAmount = NumberFormat.getInstance().parse(memory).intValue();
    return getMemoryInMi(memoryAmount, memory);
  }

  public static float getCpuInCores(String cpu) throws ParseException {
    float value = NumberFormat.getInstance().parse(cpu).floatValue();

    if (cpu != null && cpu.endsWith("m")) {
      value = value / 1000;
    }

    return value;
  }
}
