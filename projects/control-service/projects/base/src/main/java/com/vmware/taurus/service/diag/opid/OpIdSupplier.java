/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.opid;

@FunctionalInterface
public interface OpIdSupplier {
  public String getOpId();
}
