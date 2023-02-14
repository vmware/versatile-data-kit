/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
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
import com.vmware.taurus.service.graphql.model.Filter;
import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Sort;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.chrono.ChronoZonedDateTime;
import java.util.*;
import java.util.function.Predicate;

import static org.assertj.core.api.Assertions.assertThat;

class JobFieldStrategyByNextRunTest {

  private final JobFieldStrategyByNextRun strategyByNextRun = new JobFieldStrategyByNextRun();

  @Test
  void testJobNextRunStrategy_whenGettingStrategyName_shouldBeSpecific() {
    assertThat(strategyByNextRun.getStrategyName())
        .isEqualTo(JobFieldStrategyBy.NEXT_RUN_EPOCH_SECS);
  }

  @Test
  void testJobNextRunStrategy_whenAlteringFieldData_shouldModifyState() {
    String scheduleCron = "12 5 2 3 *";
    var executionTime =
        ExecutionTime.forCron(
            new CronParser(CronDefinitionBuilder.instanceDefinitionFor(CronType.UNIX))
                .parse(scheduleCron));
    Optional<ZonedDateTime> utc = executionTime.nextExecution(ZonedDateTime.now(ZoneId.of("UTC")));
    int baseTime = Math.toIntExact(utc.map(ChronoZonedDateTime::toEpochSecond).get());
    V2DataJob dataJob = new V2DataJob();
    V2DataJobConfig dataJobConfig = new V2DataJobConfig();
    V2DataJobSchedule dataJobSchedule = new V2DataJobSchedule();
    dataJobConfig.setSchedule(dataJobSchedule);
    dataJobSchedule.setScheduleCron(scheduleCron);
    dataJob.setConfig(dataJobConfig);

    assertThat(dataJob.getConfig().getSchedule().getNextRunEpochSeconds()).isZero();
    strategyByNextRun.alterFieldData(dataJob);

    int nextRunEpochSeconds = dataJob.getConfig().getSchedule().getNextRunEpochSeconds();
    assertThat(nextRunEpochSeconds).isNotZero().isEqualTo(baseTime);
  }

  @Test
  void testJobNextRunStrategy_whenAlteringFieldDataWithNullConfig_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob("12 5 2 3 *");
    dataJob.setConfig(null);

    strategyByNextRun.alterFieldData(dataJob);

    assertThat(dataJob.getConfig()).isNull();
  }

  @Test
  void testJobNextRunStrategy_whenAlteringFieldDataWithNullSchedule_shouldNotModifyState() {
    V2DataJob dataJob = createDummyJob(null);
    dataJob.setConfig(new V2DataJobConfig());

    strategyByNextRun.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getSchedule()).isNull();
  }

  @Test
  void testJobNextRunStrategy_whenAlteringFieldDataWithEmptySchedule_shouldReturnInvalidSchedule() {
    V2DataJob dataJob = createDummyJob(null);
    V2DataJobSchedule dataJobSchedule = new V2DataJobSchedule();
    dataJobSchedule.setScheduleCron(" ");
    V2DataJobConfig dataJobConfig = new V2DataJobConfig();
    dataJobConfig.setSchedule(dataJobSchedule);
    dataJob.setConfig(dataJobConfig);

    strategyByNextRun.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getSchedule().getNextRunEpochSeconds()).isEqualTo(-1);
  }

  @Test
  void
      testJobNextRunStrategy_whenAlteringFieldDataWithInvalidSchedule_shouldReturnInvalidSchedule() {
    V2DataJob dataJob = createDummyJob(null);
    V2DataJobSchedule dataJobSchedule = new V2DataJobSchedule();
    dataJobSchedule.setScheduleCron("* * ");
    V2DataJobConfig dataJobConfig = new V2DataJobConfig();
    dataJobConfig.setSchedule(dataJobSchedule);
    dataJob.setConfig(dataJobConfig);

    strategyByNextRun.alterFieldData(dataJob);

    assertThat(dataJob.getConfig().getSchedule().getNextRunEpochSeconds()).isEqualTo(-1);
  }

  @Test
  void testJobNextRunStrategy_whenComputingValidCriteriaWithoutFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter = new Filter("random", null, Sort.Direction.DESC);
    V2DataJob a = createDummyJob("5 4 * * *");
    V2DataJob b = createDummyJob("5 6 * * *"); // later than previous

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByNextRun.computeFilterCriteria(baseCriteria, baseFilter);

    assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  /**
   * This test should create two data jobs executed: a - “At 04:05 on day-of-month 1 and on Monday
   * in January.” b 0 “At 04:05 every day”
   *
   * <p>by this info we create a two dates to make a range: Next week and February 1st next year.
   * This will makes a range which should include data job "a", but excludes "b" so that test does
   * not fail each year on specific time
   */
  @Test
  void testJobNextRunStrategy_whenComputingValidCriteriaWithFilter_shouldReturnValidCriteria() {
    Criteria<V2DataJob> baseCriteria =
        new Criteria<>(Objects::nonNull, Comparator.comparing(V2DataJob::getJobName));
    Filter baseFilter =
        new Filter(
            "config.schedule.nextRunEpochSeconds",
            String.format("%d-%d", getNextWeek(), getSecondMonthOfNextYear()),
            Sort.Direction.ASC);
    V2DataJob a = createDummyJob("5 4 1 1 1");
    V2DataJob b = createDummyJob("5 6 * * *"); // later than previous

    Criteria<V2DataJob> v2DataJobCriteria =
        strategyByNextRun.computeFilterCriteria(baseCriteria, baseFilter);

    // assertThat(v2DataJobCriteria.getPredicate().test(a)).isTrue(); // TODO
    assertThat(v2DataJobCriteria.getPredicate().test(b)).isFalse();
    assertThat(v2DataJobCriteria.getComparator().compare(a, b)).isPositive();
  }

  @Test
  void testJobNextRunStrategy_whenComputingInvalidSearchProvided_shouldReturnValidPredicate() {
    Predicate<V2DataJob> predicate = strategyByNextRun.computeSearchCriteria("A");

    V2DataJob a = createDummyJob("5 6 * * *");

    assertThat(predicate.test(a)).isFalse();
  }

  private V2DataJob createDummyJob(String schedule) {
    V2DataJob job = new V2DataJob();
    V2DataJobConfig config = new V2DataJobConfig();
    V2DataJobSchedule dataJobSchedule = new V2DataJobSchedule();

    dataJobSchedule.setScheduleCron(schedule);
    config.setSchedule(dataJobSchedule);
    job.setConfig(config);

    strategyByNextRun.alterFieldData(job);
    return job;
  }

  private long getSecondMonthOfNextYear() {
    final Calendar calendar = Calendar.getInstance();
    calendar.setTime(new Date());
    calendar.set(Calendar.DAY_OF_MONTH, 1);
    calendar.set(Calendar.MONTH, 1);
    calendar.add(Calendar.YEAR, 1);

    return calendar.getTimeInMillis() / 1000;
  }

  private long getNextWeek() {
    final Calendar calendar = Calendar.getInstance();
    calendar.setTime(new Date());
    calendar.add(Calendar.WEEK_OF_YEAR, 1);

    return calendar.getTimeInMillis() / 1000;
  }
}
