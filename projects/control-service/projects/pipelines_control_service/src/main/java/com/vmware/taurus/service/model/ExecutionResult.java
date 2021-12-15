/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
public class ExecutionResult {
   private ExecutionStatus executionStatus;
   private String vdkVersion;
}
