/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql.strategy.datajob;

import com.cronutils.model.CronType;
import com.cronutils.model.definition.CronDefinitionBuilder;
import com.cronutils.model.time.ExecutionTime;
import com.cronutils.parser.CronParser;
import com.vmware.taurus.service.graphql.model.Criteria;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.model.V2DataJobSchedule;
import com.vmware.taurus.service.graphql.strategy.FieldStrategy;
import com.vmware.taurus.service.graphql.model.Filter;
import graphql.GraphqlErrorException;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.util.Pair;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import java.time.DateTimeException;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.chrono.ChronoZonedDateTime;
import java.util.Comparator;
import java.util.Optional;
import java.util.function.Predicate;

@Component
public class JobFieldStrategyByNextRun extends FieldStrategy<V2DataJob> {

  private final Logger log = LoggerFactory.getLogger(this.getClass());
  private static final long NEXT_RUN_EPOCH_SECS_INVALID_VALUE = -1L;
  private static final String DATE_SEPARATOR = "-";
  private static final CronParser CRON_PARSER =
      new CronParser(CronDefinitionBuilder.instanceDefinitionFor(CronType.UNIX));
  private static final ZoneId UTC_ZONE = ZoneId.of("UTC");
  private static final Comparator<V2DataJob> COMPARATOR_DEFAULT =
      Comparator.comparing(
          V2DataJob::getConfig,
          Comparator.comparing(
              V2DataJobConfig::getSchedule,
              Comparator.nullsFirst(
                  Comparator.comparingInt(V2DataJobSchedule::getNextRunEpochSeconds))));

  @Override
  public JobFieldStrategyBy getStrategyName() {
    return JobFieldStrategyBy.NEXT_RUN_EPOCH_SECS;
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
                int nextRun = validateAndExtractNextRun(dataJob);
                Pair<Integer, Integer> range = validateAndExtractDateRange(filter);

                return nextRun > 0 && range.getFirst() <= nextRun && nextRun <= range.getSecond();
              });
    }

    return new Criteria<>(predicate, detectSortingComparator(filter, COMPARATOR_DEFAULT, criteria));
  }

  @Override
  public Predicate<V2DataJob> computeSearchCriteria(@NonNull String searchStr) {
    return dataJob ->
        dataJob.getConfig() != null
            && dataJob.getConfig().getSchedule() != null
            && StringUtils.containsIgnoreCase(
                Integer.toString(dataJob.getConfig().getSchedule().getNextRunEpochSeconds()),
                searchStr);
  }

  /** Parse cron expression, compute the next run in UTC and alter the data job */
  @Override
  public void alterFieldData(V2DataJob dataJob) {
    V2DataJobConfig config = dataJob.getConfig();
    if (config == null) {
      return;
    }

    V2DataJobSchedule schedule = config.getSchedule();
    if (schedule == null) {
      return;
    }

    try {
      schedule.setNextRunEpochSeconds(parseNextRun(schedule.getScheduleCron()));
    } catch (IllegalArgumentException e) {
      log.warn(
          "Parsing cron expression for job {} with cron expression {} failed: {}",
          dataJob.getJobName(),
          schedule.getScheduleCron(),
          e.getMessage());
      schedule.setNextRunEpochSeconds(NEXT_RUN_EPOCH_SECS_INVALID_VALUE);
    }

    config.setSchedule(schedule);
    dataJob.setConfig(config);
  }

  private Pair<Integer, Integer> validateAndExtractDateRange(Filter filter) {
    String[] parsedStr = filter.getPattern().split(DATE_SEPARATOR);
    if (parsedStr.length != 2) {
      throw GraphqlErrorException.newErrorException()
          .message(getStrategyName().getPath() + " does not contains valid date range.")
          .build();
    }
    try {
      var start = Integer.parseInt(parsedStr[0]);
      var end = Integer.parseInt(parsedStr[1]);
      var startDate = Instant.ofEpochSecond(start);
      var endDate = Instant.ofEpochSecond(end);

      if (startDate.isAfter(endDate)) {
        throw GraphqlErrorException.newErrorException()
            .message(
                "First date of "
                    + getStrategyName().getPath()
                    + " is after the second."
                    + "The beginning date should be before the ending date")
            .build();
      }
      return Pair.of(start, end);
    } catch (NumberFormatException | DateTimeException ex) {
      throw GraphqlErrorException.newErrorException()
          .message(
              getStrategyName().getPath()
                  + " does not contains valid dates."
                  + "Correct format is \"1619460302-1619460302\"")
          .build();
    }
  }

  private int validateAndExtractNextRun(V2DataJob dataJob) {
    V2DataJobConfig config = dataJob.getConfig();
    if (config == null) {
      return -1;
    }
    V2DataJobSchedule schedule = config.getSchedule();
    if (schedule == null) {
      return -1;
    }
    return schedule.getNextRunEpochSeconds();
  }

  /**
   * Gets the next run by a cron expressions
   *
   * @throws IllegalArgumentException when invalid string is provided
   * @param scheduleCron a string that represent the expression
   * @return a long version of unix timestamp (epoch secs)
   */
  private long parseNextRun(String scheduleCron) {
    if (scheduleCron != null && !StringUtils.isBlank(scheduleCron)) {
      var executionTime = ExecutionTime.forCron(CRON_PARSER.parse(scheduleCron));
      Optional<ZonedDateTime> nextExecution =
          executionTime.nextExecution(ZonedDateTime.now(UTC_ZONE));
      return Math.toIntExact(
          nextExecution
              .map(ChronoZonedDateTime::toEpochSecond)
              .orElse(NEXT_RUN_EPOCH_SECS_INVALID_VALUE));
    }
    return NEXT_RUN_EPOCH_SECS_INVALID_VALUE;
  }
}
