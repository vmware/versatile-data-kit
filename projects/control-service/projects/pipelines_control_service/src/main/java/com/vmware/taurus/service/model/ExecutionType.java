/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum ExecutionType {
  MANUAL(0),
  SCHEDULED(1);

  @Getter private final int value;
}
