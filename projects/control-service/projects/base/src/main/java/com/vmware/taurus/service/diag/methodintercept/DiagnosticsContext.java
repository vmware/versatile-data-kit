/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.methodintercept;

import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.util.StopWatch;

/** Class encapsulating diagnostic context data. */
public class DiagnosticsContext {

  public String opId;
  public String userName;
  public JoinPoint joinPoint;
  public MethodSignature signature;
  public StopWatch stopWatch;
  // when this == this.methodResult then this value was not initialized (method threw an exception?)
  public Object methodResult;
  public Exception error;
}
