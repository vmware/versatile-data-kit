/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.SpyBean;

@SpringBootTest(classes = ControlplaneApplication.class)
public class JobImageDeployerV2Test {

  @Autowired private JobImageDeployerV2 jobImageDeployerV2;
  @SpyBean private DataJobsKubernetesService dataJobsKubernetesService;

  @Test
  public void testScheduleJob() throws ApiException {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    Mockito.doNothing().when(dataJobsKubernetesService).createCronJob(Mockito.any());

    var actualDeployment =
        jobImageDeployerV2.scheduleJob(
            dataJob, getDesiredDeployment(dataJob), null, false, false, "test-job");

    verifyActualDeployment(actualDeployment);
  }

  @Test
  public void testScheduleJob_presentInK8S() throws ApiException {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    Mockito.doNothing().when(dataJobsKubernetesService).updateCronJob(Mockito.any());

    var actualDeployment =
        jobImageDeployerV2.scheduleJob(
            dataJob, getDesiredDeployment(dataJob), null, false, true, "test-job");

    verifyActualDeployment(actualDeployment);
  }

  private void verifyActualDeployment(ActualDataJobDeployment actualDeployment) {
    Assertions.assertNotNull(actualDeployment);
    Assertions.assertNotNull(actualDeployment.getDeploymentVersionSha());
    Assertions.assertEquals("jobName", actualDeployment.getDataJobName());
    Assertions.assertEquals("testPython", actualDeployment.getPythonVersion());
    Assertions.assertEquals("testSha", actualDeployment.getGitCommitSha());
    Assertions.assertEquals("testSched", actualDeployment.getSchedule());
    Assertions.assertNotNull(actualDeployment.getResources());
    Assertions.assertEquals("user", actualDeployment.getLastDeployedBy());
    Assertions.assertTrue(actualDeployment.getEnabled());
  }

  private DesiredDataJobDeployment getDesiredDeployment(DataJob dataJob) {
    var initialDeployment = new DesiredDataJobDeployment();
    initialDeployment.setDataJob(dataJob);
    initialDeployment.setDataJobName(dataJob.getName());
    initialDeployment.setEnabled(true);
    initialDeployment.setResources(new DataJobDeploymentResources());
    initialDeployment.setSchedule("testSched");
    initialDeployment.setUserInitiated(true);
    initialDeployment.setGitCommitSha("testSha");
    initialDeployment.setPythonVersion("testPython");
    initialDeployment.setLastDeployedBy("user");

    return initialDeployment;
  }
}
