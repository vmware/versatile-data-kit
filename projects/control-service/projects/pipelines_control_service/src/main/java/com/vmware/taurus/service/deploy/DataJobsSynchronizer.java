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
import com.vmware.taurus.service.monitoring.DataJobSynchronizerMonitor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

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

  private final ThreadPoolTaskExecutor dataJobsSynchronizerTaskExecutor;

  private final DataJobSynchronizerMonitor dataJobSynchronizerMonitor;

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
      fixedDelayString =
          "${datajobs.deployment.configuration.synchronization.task.interval.ms:1000}",
      initialDelayString =
          "${datajobs.deployment.configuration.synchronization.task.initial.delay.ms:10000}")
  @SchedulerLock(name = "synchronizeDataJobsTask")
  public void synchronizeDataJobs() {
    if (!validateConfiguration()) {
      return;
    }

    log.info("Data job deployments synchronization has started.");

    Map<String, DataJob> dataJobsFromDBMap =
        StreamSupport.stream(jobsService.findAllDataJobs().spliterator(), false)
            .collect(Collectors.toMap(DataJob::getName, Function.identity()));
    Set<String> dataJobDeploymentNamesFromKubernetes;

    try {
      dataJobDeploymentNamesFromKubernetes =
          deploymentService.findAllActualDeploymentNamesFromKubernetes();
    } catch (KubernetesException e) {
      log.error(
          "Skipping data job deployment synchronization because deployment names cannot be loaded"
              + " from Kubernetes.",
          e);
      dataJobSynchronizerMonitor.countSynchronizerFailures();
      return;
    }

    Set<String> finalDataJobDeploymentNamesFromKubernetes = dataJobDeploymentNamesFromKubernetes;

    Map<String, DesiredDataJobDeployment> desiredDataJobDeploymentsFromDBMap =
        deploymentService.findAllDesiredDataJobDeployments();

    Map<String, ActualDataJobDeployment> actualDataJobDeploymentsFromDBMap =
        deploymentService.findAllActualDataJobDeployments();

    // Actual deployments that do not have an associated existing data jobs with them.
    Set<String> actualDataJobDeploymentsThatShouldBeDeleted =
        actualDataJobDeploymentsFromDBMap.keySet().stream()
            .filter(dataJobName -> !dataJobsFromDBMap.containsKey(dataJobName))
            .collect(Collectors.toSet());

    CountDownLatch countDownLatch =
        new CountDownLatch(
            dataJobsFromDBMap.size() + actualDataJobDeploymentsThatShouldBeDeleted.size());

    // Synchronizes deployments that have associated existing data jobs with them.
    // In this scenario, the deployment creation or updating has been requested.
    synchronizeDataJobs(
        dataJobsFromDBMap.keySet(),
        dataJobsFromDBMap,
        desiredDataJobDeploymentsFromDBMap,
        actualDataJobDeploymentsFromDBMap,
        finalDataJobDeploymentNamesFromKubernetes,
        countDownLatch);
    // Synchronizes deployments that do not have an associated existing data jobs with them.
    // In this scenario, the deployment deletion has been requested.
    synchronizeDataJobs(
        actualDataJobDeploymentsThatShouldBeDeleted,
        dataJobsFromDBMap,
        desiredDataJobDeploymentsFromDBMap,
        actualDataJobDeploymentsFromDBMap,
        finalDataJobDeploymentNamesFromKubernetes,
        countDownLatch);

    waitForSynchronizationCompletion(countDownLatch);
  }

  private void synchronizeDataJobs(
      Set<String> dataJobsToBeSynchronized,
      Map<String, DataJob> dataJobsFromDBMap,
      Map<String, DesiredDataJobDeployment> desiredDataJobDeploymentsFromDBMap,
      Map<String, ActualDataJobDeployment> actualDataJobDeploymentsFromDBMap,
      Set<String> finalDataJobDeploymentNamesFromKubernetes,
      CountDownLatch countDownLatch) {
    dataJobsToBeSynchronized.forEach(
        dataJobName ->
            executeDataJobSynchronizationTask(
                dataJobsFromDBMap.get(dataJobName),
                desiredDataJobDeploymentsFromDBMap.get(dataJobName),
                actualDataJobDeploymentsFromDBMap.get(dataJobName),
                finalDataJobDeploymentNamesFromKubernetes.contains(dataJobName),
                countDownLatch));
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
    } else if (actualDataJobDeployment != null) {
      deploymentService.deleteActualDeployment(actualDataJobDeployment.getDataJobName());
    }
  }

  private void executeDataJobSynchronizationTask(
      DataJob dataJob,
      DesiredDataJobDeployment desiredDataJobDeployment,
      ActualDataJobDeployment actualDataJobDeployment,
      boolean isDeploymentPresentInKubernetes,
      CountDownLatch countDownLatch) {
    dataJobsSynchronizerTaskExecutor.execute(
        () -> {
          try {
            synchronizeDataJob(
                dataJob,
                desiredDataJobDeployment,
                actualDataJobDeployment,
                isDeploymentPresentInKubernetes);
          } finally {
            countDownLatch.countDown();
          }
        });
  }

  private boolean validateConfiguration() {
    boolean valid = true;

    if (!synchronizationEnabled) {
      log.debug("Skipping the synchronization of data job deployments since it is disabled.");
      valid = false;
    }

    if (!dataJobDeploymentPropertiesConfig
        .getWriteTos()
        .contains(DataJobDeploymentPropertiesConfig.WriteTo.DB)) {
      log.debug(
          "Skipping data job deployments' synchronization due to the disabled writes to the"
              + " database.");
      valid = false;
    }

    return valid;
  }

  private void waitForSynchronizationCompletion(CountDownLatch countDownLatch) {
    try {
      log.debug(
          "Waiting for data job deployments' synchronization to complete. This process may take"
              + " some time...");
      countDownLatch.await();
      log.info("Data job deployments synchronization has successfully completed.");
      dataJobSynchronizerMonitor.countSuccessfulSynchronizerInvocation();
    } catch (InterruptedException e) {
      log.error("An error occurred during the data job deployments' synchronization", e);
      dataJobSynchronizerMonitor.countSynchronizerFailures();
    }
  }
}
