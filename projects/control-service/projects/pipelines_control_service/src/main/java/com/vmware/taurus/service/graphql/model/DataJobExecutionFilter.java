/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import com.vmware.taurus.service.model.ExecutionStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import java.time.OffsetDateTime;
import java.util.List;

@Data
@AllArgsConstructor
@Builder(toBuilder = true)
public class DataJobExecutionFilter {

  public static final String START_TIME_GTE_FIELD = "startTimeGte";
  public static final String END_TIME_GTE_FIELD = "endTimeGte";
  public static final String STATUS_IN_FIELD = "statusIn";
  public static final String JOB_NAME_IN_FIELD = "jobNameIn";
  public static final String START_TIME_LTE_FIELD = "startTimeLte";
  public static final String END_TIME_LTE_FIELD = "endTimeLte";
  public static final String TEAM_NAME_IN_FIELD = "teamNameIn";

  private OffsetDateTime startTimeGte;
  private OffsetDateTime endTimeGte;
  private List<ExecutionStatus> statusIn;
  private List<String> jobNameIn;
  private List<String> teamNameIn;
  private OffsetDateTime startTimeLte;
  private OffsetDateTime endTimeLte;
}
