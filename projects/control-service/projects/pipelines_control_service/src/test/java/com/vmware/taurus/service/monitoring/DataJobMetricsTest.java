/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tag;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.List;


@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DataJobMetricsTest {

   @Autowired
   private MeterRegistry meterRegistry;

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private DataJobMetrics dataJobMetrics;

   @Test
   @Order(1)
   public void testUpdateInfoGauges() {
      JobConfig config = new JobConfig();
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(jobsRepository.save(dataJob));

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
      Assertions.assertEquals(1, gauges.stream().findFirst().get().value());

      gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
      Assertions.assertEquals(DataJobMetrics.DEFAULT_NOTIFICATION_DELAY_PERIOD_MINUTES, gauges.stream().findFirst().get().value());
   }

   @Test
   @Order(2)
   public void testUpdateInfoGauges_whenCalledTwice_shouldNotCreateMultipleGauges() {
      JobConfig config = new JobConfig();
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(3)
   public void testUpdateInfoGauges_withoutConfiguration_shouldDoNothing() {
      var dataJob = new DataJob("data-job-no-config", null);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(4)
   public void testUpdateInfoGauges_withDifferentConfig_shouldUpdateTheGauge() {
      JobConfig config = new JobConfig();
      config.setEnableExecutionNotifications(true);
      config.setNotifiedOnJobSuccess(List.of("success@vmware.com"));
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of(DataJobMetrics.TAG_EMAIL_NOTIFIED_ON_SUCCESS, "success@vmware.com")));

      gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(5)
   public void testUpdateInfoGauges_withNullJob_shouldThrowException() {
      Assertions.assertThrows(NullPointerException.class, () -> dataJobMetrics.updateInfoGauges(null));
   }

   @Test
   @Order(6)
   public void testUpdateInfoGauges_withNewTeam_shouldUpdateTheGauge() {
      var config = new JobConfig();
      config.setTeam("my-team");
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of(DataJobMetrics.TAG_TEAM, "my-team")));
   }

   @Test
   @Order(7)
   void testUpdateInfoGauges_withDisabledExecutionNotifications_shouldExposeEmptyEmails() {
      var config = new JobConfig();
      config.setEnableExecutionNotifications(false);
      config.setNotifiedOnJobSuccess(List.of("someone@vmware.com"));
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of(DataJobMetrics.TAG_EMAIL_NOTIFIED_ON_SUCCESS, "")));
   }

   @Test
   @Order(8)
   void testUpdateInfoGauges_withNullExecutionNotifications_shouldExposeEmails() {
      var config = new JobConfig();
      config.setEnableExecutionNotifications(null);
      config.setNotifiedOnJobSuccess(List.of("someone@vmware.com"));
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(dataJob);

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of(DataJobMetrics.TAG_EMAIL_NOTIFIED_ON_SUCCESS, "someone@vmware.com")));
   }

   @Test
   @Order(9)
   void testUpdateInfoGauges_shouldUpdateNotificationDelay() {
      var config = new JobConfig();
      config.setNotificationDelayPeriodMinutes(60);
      var dataJob = new DataJob("data-job", config);

      dataJobMetrics.updateInfoGauges(jobsRepository.save(dataJob));

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertEquals(60, gauge.value());

      var expectedJob = jobsRepository.findById("data-job");
      Assertions.assertTrue(expectedJob.isPresent());
      Assertions.assertEquals(60, expectedJob.get().getJobConfig().getNotificationDelayPeriodMinutes());
   }

   @Test
   @Order(10)
   void testUpdateTerminationStatusGauge() {
      var config = new JobConfig();
      var dataJob = new DataJob("data-job", config);
      dataJob.setLatestJobTerminationStatus(ExecutionStatus.SUCCEEDED);
      dataJob.setLatestJobExecutionId("execution-id");

      dataJobMetrics.updateTerminationStatusGauge(jobsRepository.save(dataJob));

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertEquals(ExecutionStatus.SUCCEEDED.getAlertValue().doubleValue(), gauge.value());
   }


   @Test
   @Order(11)
   void testUpdateTerminationStatusGauge_withNewExecution_shouldUpdateTheGauge() {
      var config = new JobConfig();
      var dataJob = new DataJob("data-job", config);
      dataJob.setLatestJobTerminationStatus(ExecutionStatus.SUCCEEDED);
      dataJob.setLatestJobExecutionId("execution-id-new");

      dataJobMetrics.updateTerminationStatusGauge(jobsRepository.save(dataJob));

      var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertEquals(ExecutionStatus.SUCCEEDED.getAlertValue().doubleValue(), gauge.value());
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of(DataJobMetrics.TAG_EXECUTION_ID, "execution-id-new")));
   }

   @Test
   @Order(12)
   void testClearGauges_shouldClearAllGauges() {
       dataJobMetrics.clearGauges("data-job");

       var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
       Assertions.assertEquals(0, gauges.size());
       gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
       Assertions.assertEquals(0, gauges.size());
       gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
       Assertions.assertEquals(0, gauges.size());
   }
}
