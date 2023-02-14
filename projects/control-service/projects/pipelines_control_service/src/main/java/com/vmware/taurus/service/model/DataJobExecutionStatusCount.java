/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

public interface DataJobExecutionStatusCount {
  ExecutionStatus getStatus();

  int getStatusCount();

  String getJobName();
}
