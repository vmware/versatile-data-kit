/*
 * Copyright 2021-2023 VMware, Inc.
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

  private void updateDeployment(
      DeploymentStatus deploymentStatus, int deploymentProgressStartedInvocations)
      throws IOException, InterruptedException, ApiException {
    DesiredDataJobDeployment desiredDataJobDeployment = new DesiredDataJobDeployment();
    desiredDataJobDeployment.setStatus(deploymentStatus);
    DataJob dataJob = new DataJob();
    dataJob.setJobConfig(new JobConfig());
    Mockito.when(
            jobImageBuilder.buildImage(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any()))
        .thenReturn(false);

    deploymentService.updateDeployment(
        dataJob, desiredDataJobDeployment, new ActualDataJobDeployment(), true, true);

    Mockito.verify(deploymentProgress, Mockito.times(deploymentProgressStartedInvocations))
        .started(dataJob.getJobConfig(), desiredDataJobDeployment);
  }
}
