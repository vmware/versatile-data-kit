/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.mmnaseri.utils.spring.data.dsl.factory.RepositoryFactoryBuilder;
import com.vmware.taurus.datajobs.webhook.PostCreateWebHookProvider;
import com.vmware.taurus.datajobs.webhook.PostDeleteWebHookProvider;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.monitoring.DataJobInfoMonitor;
import com.vmware.taurus.service.webhook.WebHookRequestBodyProvider;
import org.junit.Test;
import org.mockito.Mockito;

import java.util.function.Supplier;

import static org.junit.Assert.*;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;

public class JobsServiceTest {

   @Test
   public void testUpdateMissing() {
      var testInst = createTestInstance();
      assertFalse(testInst.updateJob(new DataJob("hello", null, null)));
   }

   @Test
   public void testCreateConflict() {
      var testInst = createTestInstance();
      assertTrue(testInst.createJob(new DataJob("hello", new JobConfig(), null)).isCompleted());
      assertFalse(testInst.createJob(new DataJob("hello", null, null)).isCompleted());
      assertNotNull(testInst.getByName("hello").get().getJobConfig());
   }

   private JobsService createTestInstance() {
      var dataJobInfoMonitorMock = mock(DataJobInfoMonitor.class);
      doAnswer(method -> {
         Supplier<DataJob> supplier = method.getArgument(0);
         supplier.get();
         return null;
      }).when(dataJobInfoMonitorMock).updateDataJobInfo(Mockito.any());
      return new JobsService(RepositoryFactoryBuilder.builder().mock(JobsRepository.class),
              mock(DeploymentService.class),
              mock(JobCredentialsService.class),
              mock(WebHookRequestBodyProvider.class),
              mock(PostCreateWebHookProvider.class),
              mock(PostDeleteWebHookProvider.class),
              dataJobInfoMonitorMock);
   }
}
