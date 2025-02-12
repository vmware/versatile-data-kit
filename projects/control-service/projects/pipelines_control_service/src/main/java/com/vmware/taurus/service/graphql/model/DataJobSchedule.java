/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import java.util.Objects;

public class DataJobSchedule {
  private String scheduleCron;

  public DataJobSchedule scheduleCron(String scheduleCron) {
    this.scheduleCron = scheduleCron;
    return this;
  }

  public String getScheduleCron() {
    return this.scheduleCron;
  }

  public void setScheduleCron(String scheduleCron) {
    this.scheduleCron = scheduleCron;
  }

  public boolean equals(Object o) {
    if (this == o) {
      return true;
    } else if (o != null && this.getClass() == o.getClass()) {
      DataJobSchedule dataJobSchedule = (DataJobSchedule) o;
      return Objects.equals(this.scheduleCron, dataJobSchedule.scheduleCron);
    } else {
      return false;
    }
  }

  public int hashCode() {
    return Objects.hash(new Object[] {this.scheduleCron});
  }

  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DataJobSchedule {\n");
    sb.append("    scheduleCron: ").append(this.toIndentedString(this.scheduleCron)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  private String toIndentedString(Object o) {
    return o == null ? "null" : o.toString().replace("\n", "\n    ");
  }
}
