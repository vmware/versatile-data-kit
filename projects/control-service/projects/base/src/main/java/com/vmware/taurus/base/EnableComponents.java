/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.base;

/** This class holds list of properties that can used to switch on/off corresponding beans. */
public class EnableComponents {

  // Common package
  public static final String DIAGNOSTICS = "enable.diagnostic.components";

  // Server Package
  public static final String DIAGNOSTICS_INTERCEPTOR = "enable.diagnostics.interceptor.components";
}
