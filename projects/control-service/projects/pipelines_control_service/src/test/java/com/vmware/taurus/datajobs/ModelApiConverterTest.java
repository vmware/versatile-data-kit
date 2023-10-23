/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.JobConfig;
import java.time.OffsetDateTime;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class ModelApiConverterTest {

  @Test
  public void testToJobDeploymentStatus() {
    var job = createTestJob("name", "team");
    var deployment = createActualJobDeployment(job);
    var status = DeploymentModelConverter.toJobDeploymentStatus(deployment, job);

    Assertions.assertEquals("test-sha", status.getJobVersion());
    Assertions.assertEquals("3.9-secure", status.getPythonVersion());
    Assertions.assertEquals("name", status.getId());
    Assertions.assertEquals(true, status.getEnabled());
    Assertions.assertEquals("user", status.getLastDeployedBy());
    Assertions.assertEquals(OffsetDateTime.MIN.toString(), status.getLastDeployedDate());
    Assertions.assertEquals("test@mail.com", status.getContacts().getNotifiedOnJobDeploy().get(0));
    Assertions.assertEquals(1, status.getResources().getMemoryLimit());
    Assertions.assertEquals(1, status.getResources().getMemoryRequest());
    Assertions.assertEquals(1f, status.getResources().getCpuLimit());
    Assertions.assertEquals(1f, status.getResources().getCpuRequest());
  }

  @Test
  public void testToJobDeploymentStatus_emptyValues_expectNoExceptions() {
    var job = new DataJob();
    var deployment = new ActualDataJobDeployment();
    DeploymentModelConverter.toJobDeploymentStatus(deployment, job);
  }

  private DataJob createTestJob(String jobName, String teamName) {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob(teamName, jobName));
    var jobConfig = new JobConfig();
    jobConfig.setTeam(teamName);
    jobConfig.setNotifiedOnJobDeploy(List.of("test@mail.com"));
    dataJob.setJobConfig(jobConfig);
    return dataJob;
  }

  private ActualDataJobDeployment createActualJobDeployment(DataJob dataJob) {
    var deployment = new ActualDataJobDeployment();
    deployment.setGitCommitSha("actualSha");
    deployment.setDataJobName(dataJob.getName());
    deployment.setPythonVersion("3.9-secure");
    deployment.setEnabled(true);
    deployment.setLastDeployedBy("user");
    deployment.setSchedule("sched");
    deployment.setDeploymentVersionSha("test-sha");
    deployment.setLastDeployedDate(OffsetDateTime.MIN);
    var resources = new DataJobDeploymentResources();
    resources.setMemoryLimitMi(1);
    resources.setMemoryRequestMi(1);
    resources.setCpuLimitCores(1f);
    resources.setCpuRequestCores(1f);
    deployment.setResources(resources);
    return deployment;
  }
}
