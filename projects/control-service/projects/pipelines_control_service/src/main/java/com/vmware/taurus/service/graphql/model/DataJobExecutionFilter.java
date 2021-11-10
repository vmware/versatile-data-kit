/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import java.time.OffsetDateTime;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import com.vmware.taurus.service.model.ExecutionStatus;

@Data
@AllArgsConstructor
@Builder
public class DataJobExecutionFilter {

   public static final String START_TIME_GTE_FIELD = "startTimeGte";
   public static final String END_TIME_GTE_FIELD = "endTimeGte";
   public static final String STATUS_IN_FIELD = "statusIn";

   private OffsetDateTime startTimeGte;
   private OffsetDateTime endTimeGte;
   private List<ExecutionStatus> statusIn;
}
