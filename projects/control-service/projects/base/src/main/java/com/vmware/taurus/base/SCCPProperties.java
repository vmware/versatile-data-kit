/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.base;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

@Component
public class SCCPProperties {
  private @Autowired Environment environment;

  /*
   * @see SpringAppPropNames
   */
  public String getSpringProperty(String name) {
    return environment.resolvePlaceholders("${" + name + "}");
  }

  public String resolve(String expression) {
    return environment.resolvePlaceholders(expression);
  }
}
