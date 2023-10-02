/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.datajobs.webhook.PostCreateWebHookProvider;
import com.vmware.taurus.datajobs.webhook.PostDeleteWebHookProvider;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.deploy.DeploymentServiceV2;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.monitoring.DataJobMetrics;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.webhook.WebHookRequestBodyProvider;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.mock;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
public class JobsServiceTest {

  @Mock private JobsRepository jobsRepository;

  @Test
  public void testCreateUpdateMissing() {
    var testInst = createTestInstance();
    assertThrows(NullPointerException.class, () -> testInst.createJob(null).isCompleted());
    assertThrows(
        NullPointerException.class,
        () -> testInst.createJob(new DataJob("hello", null, null)).isCompleted());

    var job = new DataJob("hello", null, null);
    doAnswer(method -> 1)
        .when(jobsRepository)
        .updateDataJobLatestJobDeploymentStatusByName(
            eq(job.getName()), Mockito.any(DeploymentStatus.class));
    assertFalse(testInst.updateJob(job));
  }

  @Test
  public void testCreateConflict() {
    var testInst = createTestInstance();
    var job = new DataJob("hello", new JobConfig(), null);

    doAnswer(method -> job).when(jobsRepository).save(job);
    doAnswer(method -> 1)
        .when(jobsRepository)
        .updateDataJobLatestJobDeploymentStatusByName(
            eq(job.getName()), Mockito.any(DeploymentStatus.class));
    doAnswer(m -> Optional.of(job)).when(jobsRepository).findById(eq(job.getName()));

    assertTrue(testInst.createJob(job).isCompleted());
    assertNotNull(testInst.getByName("hello").get().getJobConfig());
  }

  private JobsService createTestInstance() {
    return new JobsService(
        jobsRepository,
        mock(DeploymentService.class),
        mock(JobCredentialsService.class),
        mock(WebHookRequestBodyProvider.class),
        mock(PostCreateWebHookProvider.class),
        mock(PostDeleteWebHookProvider.class),
        mock(DataJobMetrics.class),
        mock(DeploymentServiceV2.class),
        mock(DataJobDeploymentPropertiesConfig.class));
  }
}
