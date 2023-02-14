/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import com.vmware.taurus.service.KubernetesService;
import lombok.Getter;

public enum JobLabel {
  NAME("name"),
  VERSION("version"),
  TYPE("type"),
  EXECUTION_ID("data-job-execution-id"),
  STARTED_BY_USER("start-by-user");

  @Getter private String value;

  JobLabel(String value) {
    this.value = String.format("%s/%s", KubernetesService.LABEL_PREFIX, value);
  }
}
