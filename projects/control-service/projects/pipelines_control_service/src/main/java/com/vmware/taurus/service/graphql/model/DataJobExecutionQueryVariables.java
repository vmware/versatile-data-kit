/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

@Data
public class DataJobExecutionQueryVariables {

  public static final String PAGE_NUMBER_FIELD = "pageNumber";
  public static final String PAGE_SIZE_FIELD = "pageSize";
  public static final String FILTER_FIELD = "filter";
  public static final String ORDER_FIELD = "order";

  private Integer pageSize;
  private Integer pageNumber;
  private DataJobExecutionFilter filter;
  private DataJobExecutionOrder order;
}
