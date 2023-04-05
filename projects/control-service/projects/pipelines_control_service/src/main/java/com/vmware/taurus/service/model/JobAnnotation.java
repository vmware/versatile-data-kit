/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import com.vmware.taurus.service.KubernetesService;
import lombok.Getter;

public enum JobAnnotation {
  SCHEDULE("schedule"),
  STARTED_BY("started-by"),
  DEPLOYED_DATE("deployed-date"),
  DEPLOYED_BY("deployed-by"),
  EXECUTION_TYPE("execution-type"),
  OP_ID("op-id"),
  PYTHON_VERSION("python-version"),
  UNSCHEDULED("unscheduled");

  @Getter private String value;

  JobAnnotation(String value) {
    this.value = String.format("%s/%s", KubernetesService.LABEL_PREFIX, value);
  }
}
