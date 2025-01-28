/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import java.util.Objects;

public class DataJobResources {
  private Float cpuRequest;
  private Float cpuLimit;
  private Integer memoryRequest;
  private Integer memoryLimit;

  public DataJobResources cpuRequest(Float cpuRequest) {
    this.cpuRequest = cpuRequest;
    return this;
  }

  public Float getCpuRequest() {
    return this.cpuRequest;
  }

  public void setCpuRequest(Float cpuRequest) {
    this.cpuRequest = cpuRequest;
  }

  public DataJobResources cpuLimit(Float cpuLimit) {
    this.cpuLimit = cpuLimit;
    return this;
  }

  public Float getCpuLimit() {
    return this.cpuLimit;
  }

  public void setCpuLimit(Float cpuLimit) {
    this.cpuLimit = cpuLimit;
  }

  public DataJobResources memoryRequest(Integer memoryRequest) {
    this.memoryRequest = memoryRequest;
    return this;
  }

  public Integer getMemoryRequest() {
    return this.memoryRequest;
  }

  public void setMemoryRequest(Integer memoryRequest) {
    this.memoryRequest = memoryRequest;
  }

  public DataJobResources memoryLimit(Integer memoryLimit) {
    this.memoryLimit = memoryLimit;
    return this;
  }

  public Integer getMemoryLimit() {
    return this.memoryLimit;
  }

  public void setMemoryLimit(Integer memoryLimit) {
    this.memoryLimit = memoryLimit;
  }

  public boolean equals(Object o) {
    if (this == o) {
      return true;
    } else if (o != null && this.getClass() == o.getClass()) {
      DataJobResources dataJobResources = (DataJobResources) o;
      return Objects.equals(this.cpuRequest, dataJobResources.cpuRequest)
          && Objects.equals(this.cpuLimit, dataJobResources.cpuLimit)
          && Objects.equals(this.memoryRequest, dataJobResources.memoryRequest)
          && Objects.equals(this.memoryLimit, dataJobResources.memoryLimit);
    } else {
      return false;
    }
  }

  public int hashCode() {
    return Objects.hash(
        new Object[] {this.cpuRequest, this.cpuLimit, this.memoryRequest, this.memoryLimit});
  }

  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DataJobResources {\n");
    sb.append("    cpuRequest: ").append(this.toIndentedString(this.cpuRequest)).append("\n");
    sb.append("    cpuLimit: ").append(this.toIndentedString(this.cpuLimit)).append("\n");
    sb.append("    memoryRequest: ").append(this.toIndentedString(this.memoryRequest)).append("\n");
    sb.append("    memoryLimit: ").append(this.toIndentedString(this.memoryLimit)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  private String toIndentedString(Object o) {
    return o == null ? "null" : o.toString().replace("\n", "\n    ");
  }
}
