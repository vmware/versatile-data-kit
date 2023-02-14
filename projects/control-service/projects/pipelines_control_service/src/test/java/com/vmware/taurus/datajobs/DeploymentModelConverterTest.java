/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.service.model.JobDeployment;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class DeploymentModelConverterTest {

  @Test
  void test_mergeDeployments() {
    var oldDeployment = getTestJobDeployment();
    var newDeployment = new JobDeployment();
    newDeployment.setDataJobTeam(oldDeployment.getDataJobTeam());
    newDeployment.setDataJobName(oldDeployment.getDataJobName());
    newDeployment.setEnabled(false);
    newDeployment.setVdkVersion("new");

    var mergedDeployment = DeploymentModelConverter.mergeDeployments(oldDeployment, newDeployment);

    Assertions.assertEquals(false, mergedDeployment.getEnabled());
    Assertions.assertEquals(oldDeployment.getMode(), mergedDeployment.getMode());
    Assertions.assertEquals("new", mergedDeployment.getVdkVersion());
  }

  @Test
  void test_mergeDeployments_resources() {
    var oldDeployment = getTestJobDeployment();
    var newDeployment = new JobDeployment();
    newDeployment.setDataJobTeam(oldDeployment.getDataJobTeam());
    newDeployment.setDataJobName(oldDeployment.getDataJobName());
    newDeployment.setGitCommitSha("new-version");
    var newResources = new DataJobResources();
    newResources.setMemoryLimit(2);
    newDeployment.setResources(newResources);

    var mergedDeployment = DeploymentModelConverter.mergeDeployments(oldDeployment, newDeployment);
    Assertions.assertEquals(2, mergedDeployment.getResources().getMemoryLimit());
  }

  private static JobDeployment getTestJobDeployment() {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam("job-team");
    jobDeployment.setDataJobName("job-name");
    jobDeployment.setEnabled(true);
    jobDeployment.setResources(new DataJobResources());
    jobDeployment.setMode("mode");
    jobDeployment.setGitCommitSha("job-version");
    jobDeployment.setVdkVersion("release");
    return jobDeployment;
  }
}
