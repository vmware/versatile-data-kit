/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import lombok.Data;

import java.time.OffsetDateTime;
import java.util.List;

@Data
public class V2DataJobDeployment {
  private String id;
  private String vdkVersion;
  private String jobVersion;
  private String jobPythonVersion;
  private DataJobMode mode;
  private Boolean enabled = true;
  private DataJobContacts contacts;
  private V2DataJobSchedule schedule;
  private DataJobResources resources;
  private List<DataJobExecution> executions;
  private DataJobExecution.StatusEnum lastExecutionStatus;
  private OffsetDateTime lastExecutionTime;
  private Integer lastExecutionDuration;
  private Integer successfulExecutions;
  private Integer failedExecutions;
  private String lastDeployedBy;
  private String lastDeployedDate;
}
