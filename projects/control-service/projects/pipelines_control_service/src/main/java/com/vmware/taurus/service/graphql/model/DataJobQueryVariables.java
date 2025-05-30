/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

import java.util.List;

@Data
public class DataJobQueryVariables {
  private int pageSize;
  private int pageNumber;
  private String search;
  private List<Filter> filters;
}
