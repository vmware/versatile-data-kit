/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Set;

/**
 * This class represents a utility for synchronizing Kubernetes CronJobs with data from a database
 * to maintain the desired state in the cluster.
 *
 * <p>It provides methods to retrieve job information from a database, compare it with the current
 * state of Kubernetes Jobs, and take actions to synchronize them. This can include creating new
 * CronJobs, updating existing CronJobs, etc.
 *
 * <p>Usage: - Create an instance of this class and call the `synchronizeDataJobs` method to
 * initiate the synchronization process.
 */
@Slf4j
@RequiredArgsConstructor
@Component
public class DataJobsSynchronizer {

  private final JobsService jobsService;

  private final DeploymentServiceV2 deploymentService;

  private final DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  @Value("${datajobs.deployment.configuration.synchronization.task.enabled:false}")
  private boolean synchronizationEnabled;

  /**
   * Synchronizes Kubernetes CronJobs from the database to ensure that the cluster's state matches
   * the desired state defined in the database records.
   *
   * <p>This method retrieves job information from the database, compares it with the current state
   * of Kubernetes CronJobs in the cluster, and takes the necessary actions to synchronize them.
   * This can include creating new CronJobs, updating existing CronJobs, etc.
   */
  @Scheduled(
      fixedDelayString = "${datajobs.deployment.configuration.synchronization.task.interval:1000}",
      initialDelayString =
          "${datajobs.deployment.configuration.synchronization.task.initial.delay:10000}")
  @SchedulerLock(name = "synchronizeDataJobsTask")
  public void synchronizeDataJobs() {
    if (!synchronizationEnabled) {
      log.debug("Skipping the synchronization of data job deployments since it is disabled.");
      return;
    }

    if (!dataJobDeploymentPropertiesConfig
        .getWriteTos()
        .contains(DataJobDeploymentPropertiesConfig.WriteTo.DB)) {
      log.debug(
          "Skipping data job deployments' synchronization due to the disabled writes to the"
              + " database.");
      return;
    }

    ThreadPoolTaskExecutor taskExecutor = initializeTaskExecutor();
    Iterable<DataJob> dataJobsFromDB = jobsService.findAllDataJobs();

    Set<String> dataJobDeploymentNamesFromKubernetes;
    try {
      dataJobDeploymentNamesFromKubernetes =
          deploymentService.findAllActualDeploymentNamesFromKubernetes();
    } catch (ApiException e) {
      log.error(
          "Skipping data job deployment synchronization because deployment names cannot be loaded"
              + " from Kubernetes.",
          new KubernetesException("Cannot load cron jobs", e));
      return;
    }

    Set<String> finalDataJobDeploymentNamesFromKubernetes = dataJobDeploymentNamesFromKubernetes;

    Map<String, DesiredDataJobDeployment> desiredDataJobDeploymentsFromDBMap =
        deploymentService.findAllDesiredDataJobDeployments();

    Map<String, ActualDataJobDeployment> actualDataJobDeploymentsFromDBMap =
        deploymentService.findAllActualDataJobDeployments();

    dataJobsFromDB.forEach(
        dataJob ->
            taskExecutor.execute(
                () ->
                    synchronizeDataJob(
                        dataJob,
                        desiredDataJobDeploymentsFromDBMap.get(dataJob.getName()),
                        actualDataJobDeploymentsFromDBMap.get(dataJob.getName()),
                        finalDataJobDeploymentNamesFromKubernetes.contains(dataJob.getName()))));

    taskExecutor.shutdown();
  }

  // Default for testing purposes
  void synchronizeDataJob(
      DataJob dataJob,
      DesiredDataJobDeployment desiredDataJobDeployment,
      ActualDataJobDeployment actualDataJobDeployment,
      boolean isDeploymentPresentInKubernetes) {
    if (desiredDataJobDeployment != null) {
      deploymentService.updateDeployment(
          dataJob,
          desiredDataJobDeployment,
          actualDataJobDeployment,
          isDeploymentPresentInKubernetes);
    }
  }

  private ThreadPoolTaskExecutor initializeTaskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(5);
    executor.setMaxPoolSize(10);
    executor.setQueueCapacity(Integer.MAX_VALUE);
    executor.setAllowCoreThreadTimeOut(true);
    executor.setKeepAliveSeconds(120);
    executor.setWaitForTasksToCompleteOnShutdown(true);
    executor.initialize();

    return executor;
  }
}
