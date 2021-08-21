/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

import java.util.List;

@Data
public class ExecutionQueryVariables {
   private int executionsPageNumber;
   private int executionsPageSize;
   private List<Filter> executionsFilter;
}
