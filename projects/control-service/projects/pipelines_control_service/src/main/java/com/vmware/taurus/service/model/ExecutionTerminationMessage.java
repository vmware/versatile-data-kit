/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.Builder;
import lombok.Data;

@Builder
@Data
public class ExecutionTerminationMessage {
   private ExecutionTerminationStatus terminationStatus;
   private String vdkVersion;
}
