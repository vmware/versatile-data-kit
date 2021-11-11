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

import com.vmware.taurus.controlplane.model.data.DataJobExecution;

@Data
@AllArgsConstructor
@Builder
public class DataJobExecutionFilter {
   private OffsetDateTime startTimeGte;
   private OffsetDateTime endTimeGte;
   private List<DataJobExecution.StatusEnum> statusIn;
}
