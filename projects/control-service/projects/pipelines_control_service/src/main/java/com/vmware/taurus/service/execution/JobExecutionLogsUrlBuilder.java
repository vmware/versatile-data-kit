/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import com.vmware.taurus.service.model.DataJob;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.text.StringSubstitutor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.vmware.taurus.service.model.DataJobExecution;

/**
 * Builds logs URL for each data job execution by specified template
 * (datajobs.executions.logsUrl.template).
 *
 * <p>Supported variables which will be replaced in the template with the particular execution
 * values:
 *
 * <ul>
 *   <li>{@value VAR_PREFIX}{@value EXECUTION_ID_VAR}{@value VAR_SUFFIX}
 *   <li>{@value VAR_PREFIX}{@value OP_ID_VAR}{@value VAR_SUFFIX}
 *   <li>{@value VAR_PREFIX}{@value JOB_NAME_VAR}{@value VAR_SUFFIX}
 *   <li>{@value VAR_PREFIX}{@value START_TIME_VAR}{@value VAR_SUFFIX}
 *   <li>{@value VAR_PREFIX}{@value END_TIME_VAR}{@value VAR_SUFFIX}
 * </ul>
 *
 * Example:
 * "https://log-insight-url/li/query/stream?query=%C2%A7%C2%A7%C2%A7AND%C2%A7%C2%A7%C2%A7%C2%
 * A7{{start_time}}%C2%A7{{end_time}}%C2%A7true%C2%A7COUNT%C2%A7text:CONTAINS:{{execution_id}}*"
 */
@Slf4j
@Component
public class JobExecutionLogsUrlBuilder {

  // Default for testing purposes
  static final String VAR_PREFIX = "{{";
  static final String VAR_SUFFIX = "}}";

  static final String EXECUTION_ID_VAR = "execution_id";
  static final String OP_ID_VAR = "op_id";
  static final String JOB_NAME_VAR = "job_name";
  static final String TEAM_NAME_VAR = "team_name";
  static final String START_TIME_VAR = "start_time";
  static final String END_TIME_VAR = "end_time";

  static final String ISO_DATE_FORMAT = "iso";
  static final String UNIX_DATE_FORMAT = "unix";

  @Value("${datajobs.executions.logsUrl.template}")
  private String template;

  @Value("${datajobs.executions.logsUrl.dateFormat}")
  private String dateFormat;

  @Value("${datajobs.executions.logsUrl.startTimeOffsetSeconds}")
  private long startTimeOffsetSeconds = 0;

  @Value("${datajobs.executions.logsUrl.endTimeOffsetSeconds}")
  private long endTimeOffsetSeconds = 0;

  Clock clock = Clock.systemDefaultZone();

  public String build(DataJobExecution dataJobExecution) {
    if (StringUtils.isEmpty(template)) {
      log.warn("The property 'datajobs.executions.logsUrl.template' is empty!");
      return "";
    }

    return StringSubstitutor.replace(template, buildVars(dataJobExecution), VAR_PREFIX, VAR_SUFFIX);
  }

  private Map<String, String> buildVars(DataJobExecution dataJobExecution) {
    Map<String, String> params = new HashMap<>();

    if (dataJobExecution != null) {
      params.put(EXECUTION_ID_VAR, dataJobExecution.getId());
      params.put(OP_ID_VAR, dataJobExecution.getOpId());
      params.put(
          JOB_NAME_VAR,
          Optional.ofNullable(dataJobExecution.getDataJob())
              .map(DataJob::getName)
              .orElse(""));
      params.put(
              TEAM_NAME_VAR,
              Optional.ofNullable(dataJobExecution.getDataJob())
                      .map(j -> j.getJobConfig().getTeam())
                      .orElse(""));
      params.put(
          START_TIME_VAR, convertDate(dataJobExecution.getStartTime(), startTimeOffsetSeconds));
      params.put(END_TIME_VAR, convertDate(dataJobExecution.getEndTime(), endTimeOffsetSeconds));
    }

    return params;
  }

  private String convertDate(OffsetDateTime dateTime, Long offset) {
    String format = dateFormat;

    if (dateTime == null) {
      // if not set it to current time
      dateTime = OffsetDateTime.now(clock);
    }

    Instant offsetDateTime = dateTime.toInstant().plusSeconds(offset);

    if (StringUtils.isEmpty(format)) {
      log.warn(
          "The property 'datajobs.executions.logsUrl.dateFormat' is empty, defaults to '{}'",
          UNIX_DATE_FORMAT);
      format = UNIX_DATE_FORMAT;
    }

    switch (format) {
      case ISO_DATE_FORMAT:
        return offsetDateTime.toString();
      case UNIX_DATE_FORMAT:
        return getDateTimeUnix(offsetDateTime);
      default:
        log.warn(
            "The property 'datajobs.executions.logsUrl.dateFormat' is not correct '{}', defaults to"
                + " '{}'",
            dateFormat,
            UNIX_DATE_FORMAT);
        return getDateTimeUnix(offsetDateTime);
    }
  }

  private static String getDateTimeUnix(Instant offsetDateTime) {
    return String.valueOf(offsetDateTime.toEpochMilli());
  }
}
