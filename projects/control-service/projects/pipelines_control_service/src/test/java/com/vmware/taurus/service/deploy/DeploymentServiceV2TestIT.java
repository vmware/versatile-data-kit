/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.*;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.io.IOException;

@SpringBootTest(classes = ControlplaneApplication.class)
public class DeploymentServiceV2TestIT {

  @Autowired private DeploymentServiceV2 deploymentService;

  @MockBean private DeploymentProgress deploymentProgress;

  @MockBean private JobImageBuilder jobImageBuilder;

  @MockBean private JobImageDeployerV2 jobImageDeployer;

  @Test
  public void updateDeployment_withDesiredDeploymentStatusUserError_shouldSkipDeployment()
      throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.USER_ERROR, 0);
  }

  @Test
  public void updateDeployment_withDesiredDeploymentStatusPlatformError_shouldSkipDeployment()
      throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.PLATFORM_ERROR, 0);
  }

  @Test
  public void updateDeployment_withDesiredDeploymentStatusSuccess_shouldStartDeployment()
      throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.SUCCESS, 1);
  }

  @Test
  public void updateDeployment_withDesiredDeploymentStatusNone_shouldStartDeployment()
      throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.NONE, 1);
  }

  @Test
  public void
      updateDeployment_withDesiredDeploymentUserInitiatedDeploymentTrue_shouldSendNotification()
          throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.NONE, 1, true);

    Mockito.verify(jobImageBuilder, Mockito.times(1))
        .buildImage(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any(), Mockito.eq(true));
  }

  @Test
  public void
      updateDeployment_withDesiredDeploymentUserInitiatedDeploymentFalse_shouldNotSendNotification()
          throws IOException, InterruptedException, ApiException {
    updateDeployment(DeploymentStatus.NONE, 1, false);

    Mockito.verify(jobImageBuilder, Mockito.times(1))
        .buildImage(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any(), Mockito.eq(false));
  }

  @Test
  public void
      updateDeployment_withDesiredDeploymentEnabledFalseAndActualDeploymentEnabledTrueAndBuildImageSucceededFalse_shouldUpdateDeployment()
          throws IOException, InterruptedException, ApiException {
    updateDeployment(false, true, false, 1);
  }

  @Test
  public void
      updateDeployment_withDesiredDeploymentEnabledTrueAndActualDeploymentEnabledFalseAndBuildImageSucceededTrue_shouldUpdateDeployment()
          throws IOException, InterruptedException, ApiException {
    updateDeployment(true, false, true, 1);
  }

  @Test
  public void
      updateDeployment_withDesiredDeploymentEnabledTrueAndActualDeploymentEnabledFalseAndBuildImageSucceededFalse_shouldUpdateDeployment()
          throws IOException, InterruptedException, ApiException {
    updateDeployment(true, false, false, 0);
  }

  private void updateDeployment(
      DeploymentStatus deploymentStatus, int deploymentProgressStartedInvocations)
      throws IOException, InterruptedException, ApiException {
    updateDeployment(deploymentStatus, deploymentProgressStartedInvocations, true);
  }

  private void updateDeployment(
      DeploymentStatus deploymentStatus,
      int deploymentProgressStartedInvocations,
      boolean sendNotification)
      throws IOException, InterruptedException, ApiException {
    DesiredDataJobDeployment desiredDataJobDeployment = new DesiredDataJobDeployment();
    desiredDataJobDeployment.setStatus(deploymentStatus);
    desiredDataJobDeployment.setUserInitiated(sendNotification);
    DataJob dataJob = new DataJob();
    dataJob.setJobConfig(new JobConfig());
    Mockito.when(
            jobImageBuilder.buildImage(
                Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any()))
        .thenReturn(false);

    deploymentService.updateDeployment(
        dataJob, desiredDataJobDeployment, new ActualDataJobDeployment(), true);

    Mockito.verify(deploymentProgress, Mockito.times(deploymentProgressStartedInvocations))
        .started(dataJob.getJobConfig(), desiredDataJobDeployment);
  }

  private void updateDeployment(
      boolean desiredDeploymentEnabled,
      boolean actualDeploymentEnabled,
      boolean buildImageSucceeded,
      int deploymentProgressStartedInvocations)
      throws IOException, InterruptedException, ApiException {
    DesiredDataJobDeployment desiredDataJobDeployment = new DesiredDataJobDeployment();
    desiredDataJobDeployment.setEnabled(desiredDeploymentEnabled);
    desiredDataJobDeployment.setStatus(DeploymentStatus.NONE);

    ActualDataJobDeployment actualDeployment = new ActualDataJobDeployment();
    actualDeployment.setEnabled(actualDeploymentEnabled);

    DataJob dataJob = new DataJob();
    dataJob.setJobConfig(new JobConfig());

    Mockito.when(
            jobImageBuilder.buildImage(
                Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any()))
        .thenReturn(buildImageSucceeded);

    deploymentService.updateDeployment(dataJob, desiredDataJobDeployment, actualDeployment, true);

    Mockito.verify(jobImageDeployer, Mockito.times(deploymentProgressStartedInvocations))
        .scheduleJob(
            Mockito.any(),
            Mockito.any(),
            Mockito.any(),
            Mockito.anyBoolean(),
            Mockito.anyBoolean(),
            Mockito.anyString());
  }
}
