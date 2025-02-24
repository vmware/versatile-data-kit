/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

import java.util.List;

@Data
public class ExecutionQueryVariables {
  private int pageNumber;
  private int pageSize;
  private List<Filter> filters;
}
