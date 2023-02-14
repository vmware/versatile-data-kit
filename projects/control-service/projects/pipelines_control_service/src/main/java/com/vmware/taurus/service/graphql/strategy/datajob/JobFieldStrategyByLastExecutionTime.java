/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.Filter;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import graphql.GraphqlErrorException;
import org.springframework.data.util.Pair;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.time.DateTimeException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.util.Comparator;
import java.util.function.Predicate;

@Component
public class JobFieldStrategyByLastExecutionTime extends FieldStrategy<V2DataJob> {

  private static final String DATE_SEPARATOR = "-";
  private static final ZoneId UTC_ZONE = ZoneId.of("UTC");
  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          JobFieldStrategyByLastExecutionTime::getLastExecutionTime,
          Comparator.nullsFirst(Comparator.naturalOrder()));

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.DEPLOYMENT_LAST_EXECUTION_TIME;
  }

  /**
   * The pattern is expected to be in format like 1619460302-1619460302 (two unix times separated
   * with dash) And the first one should be before (less than) the second one
   *
   * @param criteria Existing criteria containing already chained Predicates and sorting
   * @param filter Provided filter containing information about needed sorting direction and
   *     filtering pattern.
   * @throws GraphqlErrorException if the filter pattern contains invalid format or if the first
   *     unix time is after the second one
   * @return The altered chained Predicates and comparator
   */
  @Override
  public Criteria<V2DataJob> computeFilterCriteria(
      @NonNull Criteria<V2DataJob> criteria, @NonNull Filter filter) {
    Predicate<V2DataJob> predicate = criteria.getPredicate();

    if (filterProvided(filter)) {
      predicate =
          predicate.and(
              dataJob -> {
                var lastExecutionTime = getLastExecutionTime(dataJob);
                var range = validateAndExtractDateRange(filter);

                return lastExecutionTime != null
                    && !lastExecutionTime.isBefore(range.getFirst())
                    && !lastExecutionTime.isAfter(range.getSecond());
              });
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return dataJob -> false;
  }

  private Pair<OffsetDateTime, OffsetDateTime> validateAndExtractDateRange(Filter filter) {
    String[] parsedStr = filter.getPattern().split(DATE_SEPARATOR);
    if (parsedStr.length != 2) {
      throw GraphqlErrorException.newErrorException()
          .message(getStrategyName().getPath() + " does not contain valid date range.")
          .build();
    }
    try {
      var start = Integer.parseInt(parsedStr[0]);
      var end = Integer.parseInt(parsedStr[1]);
      var startDate = OffsetDateTime.ofInstant(Instant.ofEpochSecond(start), UTC_ZONE);
      var endDate = OffsetDateTime.ofInstant(Instant.ofEpochSecond(end), UTC_ZONE);

      if (startDate.isAfter(endDate)) {
        throw GraphqlErrorException.newErrorException()
            .message(
                "First date of "
                    + getStrategyName().getPath()
                    + " is after the second."
                    + "The beginning date should be before the ending date")
            .build();
      }
      return Pair.of(startDate, endDate);
    } catch (NumberFormatException | DateTimeException ex) {
      throw GraphqlErrorException.newErrorException()
          .message(
              getStrategyName().getPath()
                  + " does not contain valid dates."
                  + "Correct format is \"1619460302-1619460302\"")
          .build();
    }
  }

  private static OffsetDateTime getLastExecutionTime(V2DataJob dataJob) {
    if (CollectionUtils.isEmpty(dataJob.getDeployments())) {
      return null;
    }
    // TODO support for multiple deployments
    return dataJob.getDeployments().stream().findFirst().orElseThrow().getLastExecutionTime();
  }
}
