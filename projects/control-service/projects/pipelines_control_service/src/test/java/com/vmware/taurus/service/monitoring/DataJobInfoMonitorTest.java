/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
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

import java.util.Collections;
import java.util.List;


@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DataJobInfoMonitorTest {

   @Autowired
   private MeterRegistry meterRegistry;

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private DataJobInfoMonitor dataJobInfoMonitor;

   @Test
   @Order(1)
   public void testUpdateDataJobInfo() {
      JobConfig config = new JobConfig();
      var dataJob = new DataJob("data-job", config);

      dataJobInfoMonitor.updateDataJobInfo(() -> jobsRepository.save(dataJob));
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());
      Assertions.assertEquals(1, gauges.stream().findFirst().get().value());
   }

   @Test
   @Order(2)
   public void testUpdateDataJobInfoTwice() {
      JobConfig config = new JobConfig();
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(3)
   public void testUpdateDataJobInfoWithoutConfiguration() {
      var dataJob = new DataJob("data-job-no-config", null);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(4)
   public void testUpdateDataJobInfoWithDifferentConfig() {
      JobConfig config = new JobConfig();
      config.setEnableExecutionNotifications(true);
      config.setNotifiedOnJobSuccess(List.of("success@vmware.com"));
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of("email_notified_on_success", "success@vmware.com")));
   }

   @Test
   @Order(5)
   public void testRemoveDataJobInfo() {
      dataJobInfoMonitor.removeDataJobInfo(() -> "data-job");
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(0, gauges.size());
   }

   @Test
   @Order(6)
   public void testUpdateDataJobsInfoWithoutJobs() {
      dataJobInfoMonitor.updateDataJobsInfo(Collections::emptyList);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(0, gauges.size());
   }

   @Test
   @Order(7)
   public void testDataJobTeamInfo() {
      var config = new JobConfig();
      config.setTeam("my-team");
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of("team", "my-team")));
   }

   @Test
   @Order(8)
   public void testRemoveDataJobInfoWithEmptyJobName() {
      dataJobInfoMonitor.removeDataJobInfo(() -> null);

      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(9)
   public void testUpdateDataJobInfoWithNullDataJob() {
      dataJobInfoMonitor.updateDataJobsInfo(() -> Collections.singletonList(null));

      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
      Assertions.assertEquals(1, gauges.size());
   }

   @Test
   @Order(10)
   void testUpdateDataJobInfoWithDisabledExecutionNotifications() {
      var config = new JobConfig();
      config.setEnableExecutionNotifications(false);
      config.setNotifiedOnJobSuccess(List.of("someone@vmware.com"));
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of("email_notified_on_success", "")));
   }

   @Test
   @Order(11)
   void testUpdateDataJobInfoWithNullExecutionNotifications() {
      var config = new JobConfig();
      config.setEnableExecutionNotifications(null);
      config.setNotifiedOnJobSuccess(List.of("someone@vmware.com"));
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> dataJob);
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertTrue(gauge.getId().getTags().contains(Tag.of("email_notified_on_success", "someone@vmware.com")));
   }

   @Test
   @Order(12)
   void testUpdateDataJobInfoWithNotificationDelay() {
      var config = new JobConfig();
      config.setNotificationDelayPeriodMinutes(60);
      var dataJob = new DataJob("data-job", config);
      dataJobInfoMonitor.updateDataJobInfo(() -> jobsRepository.save(dataJob));
      var gauges = meterRegistry.find(DataJobInfoMonitor.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();

      Assertions.assertEquals(1, gauges.size());

      var gauge = gauges.stream().findFirst().get();
      Assertions.assertEquals(60, gauge.value());

      var expectedJob = jobsRepository.findById("data-job");
      Assertions.assertTrue(expectedJob.isPresent());
      Assertions.assertEquals(60, expectedJob.get().getJobConfig().getNotificationDelayPeriodMinutes());
   }
}
