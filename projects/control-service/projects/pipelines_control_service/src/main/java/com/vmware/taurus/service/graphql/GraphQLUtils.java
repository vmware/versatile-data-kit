/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.model.ExecutionStatus;
import graphql.GraphQLException;
import lombok.experimental.UtilityClass;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.springframework.data.domain.Sort;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;

@UtilityClass
public class GraphQLUtils {

   /**
    * GraphQL's library parses json query variables to List of LinkedHashMaps. In order to use later the
    * filtering and sorting by specific field easily we convert them to list of Filters
    * @see Filter
    * @see GraphQLDataFetchers
    *
    * @param rawFilters filters object in fetched from graphql environment to convert
    * @return List of converted filters
    */
   public static List<Filter> convertFilters(List<LinkedHashMap<String, String>> rawFilters) {
      List<Filter> filters = new ArrayList<>();
      if (rawFilters != null && !rawFilters.isEmpty()) {
         rawFilters.forEach(map -> {
            if (map != null && !map.isEmpty()) {
               Sort.Direction direction = map.get("sort") == null ? null : Sort.Direction.valueOf(map.get("sort"));
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

    /**
     * This method counts Failed and Finished statuses for
     * all data job executions for a given data job and
     * returns an immutable pair of fail and success counts.
     *
     * @param dataJobName            the data job name.
     * @param jobExecutionRepository the repository to query.
     * @return ImmutablePair<Integer, Integer>, the left element is the Fail count, right Finished.
     */
    public static ImmutablePair<Integer, Integer> countFailedAndFinishedExecutions(String dataJobName,
                                                                                   JobExecutionRepository jobExecutionRepository) {

        var acceptedStatuses = List.of(ExecutionStatus.FAILED, ExecutionStatus.FINISHED);
        var statusCount = jobExecutionRepository.countFailedFinishedStatus(acceptedStatuses, List.of(dataJobName));

        int failed = 0;
        int success = 0;

        for (var status : statusCount) {
            if (status.getStatus().equals(ExecutionStatus.FAILED)) {
                failed = status.getCount();
            } else if (status.getStatus().equals(ExecutionStatus.FINISHED)) {
                success = status.getCount();
            }
        }
        return ImmutablePair.of(failed, success);
    }
}
