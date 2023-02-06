/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.kubernetes.client.openapi.ApiException;
import org.mockito.invocation.InvocationOnMock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;

import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

import static org.mockito.AdditionalAnswers.answer;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Registers a bean with a partially functional mock implementation of a {@link KubernetesService}
 * Since the mock implementation keep state of the kubernetes service resources created. If cleaning
 * that state after each test method is necessary it is a good idea to use DirtiesContext annotation
 * on the test method. See
 * https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/test/annotation/DirtiesContext.html
 */
@Profile("MockKubernetes")
@Configuration
public class MockKubernetes {

  @Bean
  @Primary
  public DataJobsKubernetesService mockDataJobsKubernetesService()
      throws ApiException, IOException, InterruptedException {
    DataJobsKubernetesService mock = mock(DataJobsKubernetesService.class);
    mockDataJobsKubernetesService(mock);
    return mock;
  }

  @Bean
  @Primary
  public ControlKubernetesService mockControlKubernetesService()
      throws ApiException, IOException, InterruptedException {
    ControlKubernetesService mock = mock(ControlKubernetesService.class);
    mockKubernetesService(mock);
    return mock;
  }

  @Bean
  @Primary
  public TaskExecutor taskExecutor() {
    // Deployment methods are non-blocking (Async) which makes them harder to test.
    // Making them sync for the purposes of this test.
    return new SyncTaskExecutor();
  }


  private void mockKubernetesService(KubernetesService mock)
          throws ApiException, IOException, InterruptedException {
    // By defautl beans are singleton scoped so we are sure this will be called once
    // hence it's safe to keep the variables here isntead of static.
    final Map<String, Map<String, byte[]>> secrets = new ConcurrentHashMap<>();

    final Map<String, InvocationOnMock> jobs = new ConcurrentHashMap<>();

    when(mock.getSecretData(any()))
            .thenAnswer(inv -> secrets.getOrDefault(inv.getArgument(0), Collections.emptyMap()));
    doAnswer(answer(secrets::put)).when(mock).saveSecretData(any(), any());
    doAnswer(inv -> secrets.remove(inv.getArgument(0))).when(mock).removeSecretData(any());

    doAnswer(inv -> jobs.put(inv.getArgument(0), inv))
            .when(mock)
            .createJob(
                    anyString(),
                    anyString(),
                    anyBoolean(),
                    anyBoolean(),
                    any(),
                    any(),
                    any(),
                    any(),
                    anyString(),
                    any(),
                    any(),
                    anyLong(),
                    anyLong(),
                    anyLong(),
                    anyString(),
                    anyString());
    doAnswer(inv -> jobs.remove(inv.getArgument(0))).when(mock).deleteJob(anyString());

    doAnswer(
            inv -> {
              String jobName = inv.getArgument(0);
              if (jobs.containsKey(jobName)) {
                if (jobName.startsWith("failure-")) {
                  return new KubernetesService.JobStatusCondition(
                          false, "Status", "Job name starts with 'failure-'", "", 0);
                } else {
                  return new KubernetesService.JobStatusCondition(true, "Status", "", "", 0);
                }
              }
              return new KubernetesService.JobStatusCondition(false, null, "No such job", "", 0);
            })
            .when(mock)
            .watchJob(anyString(), anyInt(), any());

    doAnswer(inv -> "logs").when(mock).getJobLogs(anyString(), anyInt());
  }
  /**
   * Mocks interactions with KubernetesService as much as necessary for unit testing purpose.
   *
   * <p>NOTES: If job name starts with 'failure-' (e.g failure-my-job) - then Job status will be
   * fail otherwise it's success.
   */
  private void mockDataJobsKubernetesService(DataJobsKubernetesService mock)
      throws ApiException, IOException, InterruptedException {
    mockKubernetesService(mock);
    final Map<String, InvocationOnMock> crons = new ConcurrentHashMap<>();

    doAnswer(inv -> crons.put(inv.getArgument(0), inv))
            .when(mock)
            .createCronJob(
                    anyString(),
                    anyString(),
                    any(),
                    anyString(),
                    anyBoolean(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any());
    doAnswer(inv -> crons.put(inv.getArgument(0), inv))
            .when(mock)
            .createCronJob(
                    anyString(),
                    anyString(),
                    any(),
                    anyString(),
                    anyBoolean(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    anyList());
    doAnswer(inv -> crons.put(inv.getArgument(0), inv))
            .when(mock)
            .updateCronJob(
                    anyString(),
                    anyString(),
                    any(),
                    anyString(),
                    anyBoolean(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any(),
                    any());
    doAnswer(inv -> crons.keySet()).when(mock).listCronJobs();
    doAnswer(inv -> crons.remove(inv.getArgument(0))).when(mock).deleteCronJob(anyString());
    doAnswer(
            inv -> {
              JobDeploymentStatus deployment = null;
              if (crons.containsKey(inv.getArgument(0))) {
                deployment = new JobDeploymentStatus();
                deployment.setMode("release");
                deployment.setCronJobName(inv.getArgument(0));
                deployment.setImageName("image-name");
                deployment.setGitCommitSha("foo");
              }
              return Optional.ofNullable(deployment);
            })
            .when(mock)
            .readCronJob(anyString());
  }
}
