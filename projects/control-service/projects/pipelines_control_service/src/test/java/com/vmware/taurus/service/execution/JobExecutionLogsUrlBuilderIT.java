/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.text.MessageFormat;
import java.time.OffsetDateTime;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.util.ReflectionTestUtils;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.JobConfig;

@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionLogsUrlBuilderIT {

   private static final String TEST_EXECUTION_ID = "test-job-name-1634127142";
   private static final String TEST_JOB_NAME = "test-job-name";
   private static final String TEST_OP_ID = "test-op-id-1634127142";
   private static final OffsetDateTime TEST_START_TIME = OffsetDateTime.now();
   private static final OffsetDateTime TEST_END_TIME = OffsetDateTime.now();

   private static final String LOGS_URL_TEMPLATE =
         "https://log-insight-base-url/li/query/stream?query=%C2%A7%C2%A7%C2%A7AND%C" +
               "2%A7%C2%A7%C2%A7%C2%A7{0}%C2%A7{1}%C2%A7true%C2%A7COUNT%C2%A7*%C2%A7" +
               "timestamp%C2%A7pageSortPreference:%7B%22sortBy%22%3A%22-{2}-{3}-" +
               "ingest_timestamp%22%2C%22sortOrder%22%3A%22DESC%22%7D%C2%A7" +
               "alertDefList:%5B%5D%C2%A7partitions:%C2%A7%C2%A7text:CONTAINS:{4}*";

   private static final String LOGS_URL_TEMPLATE_RAW =
         MessageFormat.format(
               LOGS_URL_TEMPLATE,
               buildVarPlaceholder(JobExecutionLogsUrlBuilder.START_TIME_VAR),
               buildVarPlaceholder(JobExecutionLogsUrlBuilder.END_TIME_VAR),
               buildVarPlaceholder(JobExecutionLogsUrlBuilder.JOB_NAME_VAR),
               buildVarPlaceholder(JobExecutionLogsUrlBuilder.OP_ID_VAR),
               buildVarPlaceholder(JobExecutionLogsUrlBuilder.EXECUTION_ID_VAR));

   @Autowired
   private JobExecutionLogsUrlBuilder logsUrlBuilder;

   @Test
   public void testBuild_allParamsAndDataFormatUnix_shouldReturnLogsUrl() {
      String expectedLogsUrl = buildExpectedLogsUrlDateFormatUnix();
      assertLogsUrlValid(LOGS_URL_TEMPLATE_RAW, JobExecutionLogsUrlBuilder.UNIX_DATE_FORMAT, expectedLogsUrl);
   }

   @Test
   public void testBuild_allParamsAndDataFormatIso_shouldReturnLogsUrl() {
      String expectedLogsUrl = buildExpectedLogsUrlDateFormatIso();
      assertLogsUrlValid(LOGS_URL_TEMPLATE_RAW, JobExecutionLogsUrlBuilder.ISO_DATE_FORMAT, expectedLogsUrl);
   }

   @Test
   public void testBuild_extraParamAndDataFormatUnix_shouldReturnLogsUrl() {
      String expectedLogsUrl = buildExpectedLogsUrlDateFormatUnix() + "{{abc}}";
      assertLogsUrlValid(LOGS_URL_TEMPLATE_RAW + "{{abc}}", JobExecutionLogsUrlBuilder.UNIX_DATE_FORMAT, expectedLogsUrl);
   }

   @Test
   public void testBuild_partialParamsAndDataFormatUnix_shouldReturnLogsUrl() {
      String logsUrlRaw = MessageFormat.format(
            LOGS_URL_TEMPLATE,
            buildVarPlaceholder(JobExecutionLogsUrlBuilder.START_TIME_VAR),
            buildVarPlaceholder(JobExecutionLogsUrlBuilder.END_TIME_VAR),
            buildVarPlaceholder(JobExecutionLogsUrlBuilder.JOB_NAME_VAR),
            buildVarPlaceholder(JobExecutionLogsUrlBuilder.OP_ID_VAR),
            "");
      String expectedLogsUrl = MessageFormat.format(LOGS_URL_TEMPLATE,
            String.valueOf(TEST_START_TIME.toInstant().toEpochMilli()),
            String.valueOf(TEST_END_TIME.toInstant().toEpochMilli()),
            TEST_JOB_NAME,
            TEST_OP_ID,
            "");

      assertLogsUrlValid(logsUrlRaw, JobExecutionLogsUrlBuilder.UNIX_DATE_FORMAT, expectedLogsUrl);
   }

   @Test
   public void testBuild_emptyLogsUrlTemplate_shouldReturnEmptyLogsUrl() {
      assertLogsUrlValid("", JobExecutionLogsUrlBuilder.UNIX_DATE_FORMAT, "");
   }

   @Test
   public void testBuild_nullLogsUrlTemplate_shouldReturnEmptyLogsUrl() {
      assertLogsUrlValid(null, JobExecutionLogsUrlBuilder.UNIX_DATE_FORMAT, "");
   }

   @Test
   public void testBuild_nullLogsUrlDateFormat_shouldReturnLogsUrlWithDateFormatUnix() {
      String expectedLogsUrl = buildExpectedLogsUrlDateFormatUnix();
      assertLogsUrlValid(LOGS_URL_TEMPLATE_RAW, null, expectedLogsUrl);
   }

   @Test
   public void testBuild_emptyLogsUrlDateFormat_shouldReturnLogsUrlWithDateFormatUnix() {
      String expectedLogsUrl = buildExpectedLogsUrlDateFormatUnix();
      assertLogsUrlValid(LOGS_URL_TEMPLATE_RAW, "", expectedLogsUrl);
   }

   private static String buildVarPlaceholder(String var) {
      return JobExecutionLogsUrlBuilder.VAR_PREFIX + var + JobExecutionLogsUrlBuilder.VAR_SUFFIX;
   }

   private static String buildExpectedLogsUrlDateFormatUnix() {
      return MessageFormat.format(
            LOGS_URL_TEMPLATE,
            String.valueOf(TEST_START_TIME.toInstant().toEpochMilli()),
            String.valueOf(TEST_END_TIME.toInstant().toEpochMilli()),
            TEST_JOB_NAME,
            TEST_OP_ID,
            TEST_EXECUTION_ID);
   }

   private static String buildExpectedLogsUrlDateFormatIso() {
      return MessageFormat.format(
            LOGS_URL_TEMPLATE,
            TEST_START_TIME.toInstant().toString(),
            TEST_END_TIME.toInstant().toString(),
            TEST_JOB_NAME,
            TEST_OP_ID,
            TEST_EXECUTION_ID);
   }

   private void assertLogsUrlValid(String logsUrlTemplate, String logsUrlDateFormat, String expectedLogsUrl) {
      ReflectionTestUtils.setField(logsUrlBuilder, "template", logsUrlTemplate);
      ReflectionTestUtils.setField(logsUrlBuilder, "dateFormat", logsUrlDateFormat);

      DataJobExecution execution = DataJobExecution
            .builder()
            .id(TEST_EXECUTION_ID)
            .dataJob(new DataJob(TEST_JOB_NAME, new JobConfig()))
            .opId(TEST_OP_ID)
            .startTime(TEST_START_TIME)
            .endTime(TEST_END_TIME)
            .build();

      String actualLogsUrl = logsUrlBuilder.build(execution);
      Assertions.assertEquals(expectedLogsUrl, actualLogsUrl);
   }
}
