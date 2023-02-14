/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.diag.OperationContext;
import graphql.GraphQL;
import graphql.spring.web.servlet.JsonSerializer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(MockitoExtension.class)
class GraphQLJobsQueryServiceTest {

  @Mock private GraphQL graphQL;
  @Mock private JsonSerializer jsonSerializer;
  @Mock private OperationContext operationContext;

  private GraphQLJobsQueryService queryService;

  @BeforeEach
  void beforeEach() {
    queryService = new GraphQLJobsQueryService(graphQL, jsonSerializer, operationContext);
  }

  @Test
  void testQueryService_whenConvertingNullString_shouldReturnEmptyMap() {
    Map<String, Object> stringObjectMap = queryService.convertVariablesJson(null);

    assertThat(stringObjectMap).isEmpty();
  }
}
