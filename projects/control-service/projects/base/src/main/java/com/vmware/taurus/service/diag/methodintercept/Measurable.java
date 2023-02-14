/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.methodintercept;

import java.lang.annotation.*;

/** Use this annotation to enable diagnostics collection on class or methods. */
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Repeatable(MeasurableContainer.class)
public @interface Measurable {

  /*
   * the arg ordinal (starting at 0) whose value should be included in the metrics.
   * Each argument will be serialized in json if possible, if not it will fall-back to toString()
   * An ordinal is used since the Aspect doesn't actually have access to parameter names.
   */
  int includeArg() default -1;

  /*
   * The name of the argument at index (as specified by includeArg).
   * If no name is specified at given index then "arg" is used.
   */
  String argName() default "arg";

  /*
   * List of tags - these are just passed through - to make reporting easier.
   */
  String[] tags() default {};
}
