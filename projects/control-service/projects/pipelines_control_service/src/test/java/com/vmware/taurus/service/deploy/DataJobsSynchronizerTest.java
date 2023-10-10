/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.util.Collections;
import java.util.Set;

@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK, classes = ServiceApp.class)
public class DataJobsSynchronizerTest {

  @Autowired private DataJobsSynchronizer dataJobsSynchronizer;

  @MockBean private DeploymentServiceV2 deploymentService;

  @MockBean private DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  @Test
  void
      synchronizeDataJobs_loadDeploymentNamesFromKubernetesReturnsValue_shouldFinishSynchronization()
          throws ApiException {
    enableSynchronizationProcess();

    Mockito.when(deploymentService.findAllActualDeploymentNamesFromKubernetes())
        .thenReturn(Collections.emptySet());

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(1))
        .findAllActualDeploymentNamesFromKubernetes();

    Mockito.verify(deploymentService, Mockito.times(1)).findAllActualDataJobDeployments();
  }

  @Test
  void
      synchronizeDataJobs_loadDeploymentNamesFromKubernetesThrowsApiException_shouldSkipSynchronization()
          throws ApiException {
    enableSynchronizationProcess();

    Mockito.when(deploymentService.findAllActualDeploymentNamesFromKubernetes())
        .thenThrow(new ApiException());

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(1))
        .findAllActualDeploymentNamesFromKubernetes();

    Mockito.verify(deploymentService, Mockito.times(0)).findAllActualDataJobDeployments();
  }

  @Test
  void synchronizeDataJobs_synchronizationEnabledFalseAndWriteToDbTrue_shouldSkipSynchronization()
      throws ApiException {
    initSynchronizationProcessConfig(false, true);

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(0))
        .findAllActualDeploymentNamesFromKubernetes();
  }

  @Test
  void synchronizeDataJobs_synchronizationEnabledFalseAndWriteToDbFalse_shouldSkipSynchronization()
      throws ApiException {
    initSynchronizationProcessConfig(false, false);

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(0))
        .findAllActualDeploymentNamesFromKubernetes();
  }

  @Test
  void synchronizeDataJobs_synchronizationEnabledTrueAndWriteToDbTrue_shouldFinishSynchronization()
      throws ApiException {
    initSynchronizationProcessConfig(true, true);

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(1))
        .findAllActualDeploymentNamesFromKubernetes();
  }

  @Test
  void synchronizeDataJobs_synchronizationEnabledTrueAndWriteToDbFalse_shouldSkipSynchronization()
      throws ApiException {
    initSynchronizationProcessConfig(true, false);

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(0))
        .findAllActualDeploymentNamesFromKubernetes();
  }

  @Test
  void synchronizeDataJob_desiredDeploymentNullAndActualDeploymentNull_shouldSkipSynchronization() {
    DataJob dataJob = new DataJob();
    dataJob.setName("test-job-name");
    boolean isDeploymentPresentInKubernetes = false;
    DesiredDataJobDeployment desiredDataJobDeployment = null;
    ActualDataJobDeployment actualDataJobDeployment = null;

    dataJobsSynchronizer.synchronizeDataJob(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);

    Mockito.verify(deploymentService, Mockito.times(0))
            .updateDeployment(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);
    Mockito.verify(deploymentService, Mockito.times(0))
            .deleteActualDeployment(dataJob.getName());
  }

  @Test
  void synchronizeDataJob_desiredDeploymentNullAndActualDeploymentNotNull_shouldDeleteJobDeployment() {
    DataJob dataJob = new DataJob();
    dataJob.setName("test-job-name");
    boolean isDeploymentPresentInKubernetes = true;
    DesiredDataJobDeployment desiredDataJobDeployment = null;
    ActualDataJobDeployment actualDataJobDeployment = new ActualDataJobDeployment();

    dataJobsSynchronizer.synchronizeDataJob(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);

    Mockito.verify(deploymentService, Mockito.times(0))
            .updateDeployment(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);
    Mockito.verify(deploymentService, Mockito.times(1))
            .deleteActualDeployment(dataJob.getName());
  }

  @Test
  void synchronizeDataJob_desiredDeploymentNotNullAndActualDeploymentNotNull_shouldUpdateJobDeployment() {
    DataJob dataJob = new DataJob();
    dataJob.setName("test-job-name");
    boolean isDeploymentPresentInKubernetes = true;
    DesiredDataJobDeployment desiredDataJobDeployment = new DesiredDataJobDeployment();
    ActualDataJobDeployment actualDataJobDeployment = new ActualDataJobDeployment();

    dataJobsSynchronizer.synchronizeDataJob(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);

    Mockito.verify(deploymentService, Mockito.times(1))
            .updateDeployment(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);
    Mockito.verify(deploymentService, Mockito.times(0))
            .deleteActualDeployment(dataJob.getName());
  }

  @Test
  void synchronizeDataJob_desiredDeploymentNotNullAndActualDeploymentNull_shouldUpdateJobDeployment() {
    DataJob dataJob = new DataJob();
    dataJob.setName("test-job-name");
    boolean isDeploymentPresentInKubernetes = true;
    DesiredDataJobDeployment desiredDataJobDeployment = new DesiredDataJobDeployment();
    ActualDataJobDeployment actualDataJobDeployment = null;

    dataJobsSynchronizer.synchronizeDataJob(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);

    Mockito.verify(deploymentService, Mockito.times(1))
            .updateDeployment(dataJob, desiredDataJobDeployment, actualDataJobDeployment, isDeploymentPresentInKubernetes);
    Mockito.verify(deploymentService, Mockito.times(0))
            .deleteActualDeployment(dataJob.getName());
  }

  void enableSynchronizationProcess() {
    initSynchronizationProcessConfig(true, true);
  }

  void initSynchronizationProcessConfig(boolean synchronizationEnabled, boolean writeToDB) {
    ReflectionTestUtils.setField(
        dataJobsSynchronizer, "synchronizationEnabled", synchronizationEnabled);
    Mockito.when(dataJobDeploymentPropertiesConfig.getWriteTos())
        .thenReturn(
            writeToDB
                ? Set.of(DataJobDeploymentPropertiesConfig.WriteTo.DB)
                : Collections.emptySet());
  }
}
