/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.exception;

public enum ExecutionCancellationFailureReason {
  DataJobNotFound,
  DataJobExecutionNotFound,
  ExecutionNotRunning
}
