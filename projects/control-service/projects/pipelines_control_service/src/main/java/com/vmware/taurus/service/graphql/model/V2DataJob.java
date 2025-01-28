/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

import java.util.List;

@Data
public class V2DataJob {
  private String jobName;
  private V2DataJobConfig config;
  private List<V2DataJobDeployment> deployments;
}
