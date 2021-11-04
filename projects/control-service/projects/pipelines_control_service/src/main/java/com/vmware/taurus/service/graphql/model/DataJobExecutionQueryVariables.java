/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.model;

import lombok.Data;

@Data
public class DataJobExecutionQueryVariables {
   private Integer pageSize;
   private Integer pageNumber;
   private DataJobExecutionFilter filter;
   private DataJobExecutionOrder order;
}
