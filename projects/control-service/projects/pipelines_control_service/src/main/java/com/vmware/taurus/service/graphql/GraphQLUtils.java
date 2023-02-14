/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.graphql.model.Filter;
import graphql.GraphQLException;
import lombok.experimental.UtilityClass;
import org.springframework.data.domain.Sort;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Set;

@UtilityClass
public class GraphQLUtils {

  public static final String JOBS_QUERY = "jobs";
  public static final String EXECUTIONS_QUERY = "executions";
  public static final Set<String> QUERIES = Set.of(JOBS_QUERY, EXECUTIONS_QUERY);

  /**
   * GraphQL's library parses json query variables to List of LinkedHashMaps. In order to use later
   * the filtering and sorting by specific field easily we convert them to list of Filters
   *
   * @see Filter
   * @see GraphQLDataFetchers
   * @param rawFilters filters object in fetched from graphql environment to convert
   * @return List of converted filters
   */
  public static List<Filter> convertFilters(List<LinkedHashMap<String, String>> rawFilters) {
    List<Filter> filters = new ArrayList<>();
    if (rawFilters != null && !rawFilters.isEmpty()) {
      rawFilters.forEach(
          map -> {
            if (map != null && !map.isEmpty()) {
              Sort.Direction direction =
                  map.get("sort") == null ? null : Sort.Direction.valueOf(map.get("sort"));
              filters.add(new Filter(map.get("property"), map.get("pattern"), direction));
            }
          });
    }
    return filters;
  }

  public static void validatePageInput(int pageSize, int pageNumber) {
    if (pageSize < 1) {
      throw new GraphQLException("Page size cannot be less than 1");
    }
    if (pageNumber < 1) {
      throw new GraphQLException("Page cannot be less than 1");
    }
  }
}
