/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import java.time.OffsetDateTime;
import java.util.Objects;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.format.annotation.DateTimeFormat.ISO;

public class DataJobDeployment {
  private String vdkVersion;
  private String jobVersion;
  private String jobPythonVersion;
  private DataJobMode mode;
  private String id;
  private Boolean enabled;
  private String deployedBy;

  @DateTimeFormat(iso = ISO.DATE_TIME)
  private OffsetDateTime deployedDate;

  private DataJobSchedule schedule;
  private DataJobResources resources;

  public DataJobDeployment vdkVersion(String vdkVersion) {
    this.vdkVersion = vdkVersion;
    return this;
  }

  public String getVdkVersion() {
    return this.vdkVersion;
  }

  public void setVdkVersion(String vdkVersion) {
    this.vdkVersion = vdkVersion;
  }

  public DataJobDeployment jobVersion(String jobVersion) {
    this.jobVersion = jobVersion;
    return this;
  }

  public String getJobVersion() {
    return this.jobVersion;
  }

  public void setJobVersion(String jobVersion) {
    this.jobVersion = jobVersion;
  }

  public DataJobDeployment jobPythonVersion(String jobPythonVersion) {
    this.jobPythonVersion = jobPythonVersion;
    return this;
  }

  public String getJobPythonVersion() {
    return this.jobPythonVersion;
  }

  public void setJobPythonVersion(String jobPythonVersion) {
    this.jobPythonVersion = jobPythonVersion;
  }

  public DataJobDeployment mode(DataJobMode mode) {
    this.mode = mode;
    return this;
  }

  public DataJobMode getMode() {
    return this.mode;
  }

  public void setMode(DataJobMode mode) {
    this.mode = mode;
  }

  public DataJobDeployment id(String id) {
    this.id = id;
    return this;
  }

  public String getId() {
    return this.id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public DataJobDeployment enabled(Boolean enabled) {
    this.enabled = enabled;
    return this;
  }

  public Boolean getEnabled() {
    return this.enabled;
  }

  public void setEnabled(Boolean enabled) {
    this.enabled = enabled;
  }

  public DataJobDeployment deployedBy(String deployedBy) {
    this.deployedBy = deployedBy;
    return this;
  }

  public String getDeployedBy() {
    return this.deployedBy;
  }

  public void setDeployedBy(String deployedBy) {
    this.deployedBy = deployedBy;
  }

  public DataJobDeployment deployedDate(OffsetDateTime deployedDate) {
    this.deployedDate = deployedDate;
    return this;
  }

  public OffsetDateTime getDeployedDate() {
    return this.deployedDate;
  }

  public void setDeployedDate(OffsetDateTime deployedDate) {
    this.deployedDate = deployedDate;
  }

  public DataJobDeployment schedule(DataJobSchedule schedule) {
    this.schedule = schedule;
    return this;
  }

  public DataJobSchedule getSchedule() {
    return this.schedule;
  }

  public void setSchedule(DataJobSchedule schedule) {
    this.schedule = schedule;
  }

  public DataJobDeployment resources(DataJobResources resources) {
    this.resources = resources;
    return this;
  }

  public DataJobResources getResources() {
    return this.resources;
  }

  public void setResources(DataJobResources resources) {
    this.resources = resources;
  }

  public boolean equals(Object o) {
    if (this == o) {
      return true;
    } else if (o != null && this.getClass() == o.getClass()) {
      DataJobDeployment dataJobDeployment = (DataJobDeployment) o;
      return Objects.equals(this.vdkVersion, dataJobDeployment.vdkVersion)
          && Objects.equals(this.jobVersion, dataJobDeployment.jobVersion)
          && Objects.equals(this.jobPythonVersion, dataJobDeployment.jobPythonVersion)
          && Objects.equals(this.mode, dataJobDeployment.mode)
          && Objects.equals(this.id, dataJobDeployment.id)
          && Objects.equals(this.enabled, dataJobDeployment.enabled)
          && Objects.equals(this.deployedBy, dataJobDeployment.deployedBy)
          && Objects.equals(this.deployedDate, dataJobDeployment.deployedDate)
          && Objects.equals(this.schedule, dataJobDeployment.schedule)
          && Objects.equals(this.resources, dataJobDeployment.resources);
    } else {
      return false;
    }
  }

  public int hashCode() {
    return Objects.hash(
        new Object[] {
          this.vdkVersion,
          this.jobVersion,
          this.jobPythonVersion,
          this.mode,
          this.id,
          this.enabled,
          this.deployedBy,
          this.deployedDate,
          this.schedule,
          this.resources
        });
  }

  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class DataJobDeployment {\n");
    sb.append("    vdkVersion: ").append(this.toIndentedString(this.vdkVersion)).append("\n");
    sb.append("    jobVersion: ").append(this.toIndentedString(this.jobVersion)).append("\n");
    sb.append("    jobPythonVersion: ")
        .append(this.toIndentedString(this.jobPythonVersion))
        .append("\n");
    sb.append("    mode: ").append(this.toIndentedString(this.mode)).append("\n");
    sb.append("    id: ").append(this.toIndentedString(this.id)).append("\n");
    sb.append("    enabled: ").append(this.toIndentedString(this.enabled)).append("\n");
    sb.append("    deployedBy: ").append(this.toIndentedString(this.deployedBy)).append("\n");
    sb.append("    deployedDate: ").append(this.toIndentedString(this.deployedDate)).append("\n");
    sb.append("    schedule: ").append(this.toIndentedString(this.schedule)).append("\n");
    sb.append("    resources: ").append(this.toIndentedString(this.resources)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  private String toIndentedString(Object o) {
    return o == null ? "null" : o.toString().replace("\n", "\n    ");
  }
}
