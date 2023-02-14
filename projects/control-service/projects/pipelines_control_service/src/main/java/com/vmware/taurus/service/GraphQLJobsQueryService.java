/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.diag.OperationContext;
import graphql.ExecutionInput;
import graphql.ExecutionResult;
import graphql.GraphQL;
import graphql.execution.ExecutionId;
import graphql.spring.web.servlet.JsonSerializer;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.Map;

@Service
@AllArgsConstructor
public class GraphQLJobsQueryService {

  public static final String DEFAULT_QUERY =
      "{"
          + "  jobs(pageNumber: 1, pageSize: 20, filter: []) {"
          + "    content {"
          + "      jobName"
          + "      config {"
          + "        team"
          + "        description"
          + "        schedule {"
          + "          scheduleCron"
          + "        }"
          + "      }"
          + "    }"
          + "    totalPages"
          + "    totalItems"
          + "  }"
          + "}";

  private final GraphQL graphQL;
  private final JsonSerializer jsonSerializer;
  private final OperationContext operationContext;

  @SuppressWarnings("unchecked")
  public Map<String, Object> convertVariablesJson(String jsonMap) {
    if (jsonMap == null) {
      return Collections.emptyMap();
    }
    // find a better way instead of suppressing warnings
    return jsonSerializer.deserialize(jsonMap, Map.class);
  }

  public ExecutionResult executeRequest(
      String query, String operationName, Map<String, Object> variables) {
    return graphQL.execute(
        ExecutionInput.newExecutionInput()
            .variables(variables)
            .query(query)
            .executionId(ExecutionId.from(operationContext.getOpId()))
            .operationName(operationName == null ? "" : operationName.trim().replace("\"", ""))
            .build());
  }
}
