/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

public enum DataJobMode {
  TESTING("testing"),
  RELEASE("release");

  private String value;

  private DataJobMode(String value) {
    this.value = value;
  }

  @JsonValue
  public String getValue() {
    return this.value;
  }

  public String toString() {
    return String.valueOf(this.value);
  }

  @JsonCreator
  public static DataJobMode fromValue(String value) {
    DataJobMode[] var1 = values();
    int var2 = var1.length;

    for (int var3 = 0; var3 < var2; ++var3) {
      DataJobMode b = var1[var3];
      if (b.value.equals(value)) {
        return b;
      }
    }

    throw new IllegalArgumentException("Unexpected value '" + value + "'");
  }
}
