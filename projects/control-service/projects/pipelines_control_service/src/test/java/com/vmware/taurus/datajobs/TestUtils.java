/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.*;

public class TestUtils {

   //@NotNull
   public static DataJob getDataJob(String teamName, String name) {
      var job = new DataJob();
      job.setJobName(name);
      job.setTeam(teamName);
      var dataJobConfig = new DataJobConfig();
      dataJobConfig.setGenerateKeytab(true);
      dataJobConfig.setSchedule(new DataJobSchedule());
      dataJobConfig.getSchedule().setScheduleCron("15 10 * * *");
      dataJobConfig.setContacts(new DataJobContacts());
      dataJobConfig.setDbDefaultType("");
      job.setConfig(dataJobConfig);
      return job;
   }

   public static DataJobDeployment getDataJobDeployment(String deploymentId, String jobVersion) {
      var jobDeployment = new DataJobDeployment();
      jobDeployment.setVdkVersion("");
      jobDeployment.setJobVersion(jobVersion);
      jobDeployment.setMode(DataJobMode.RELEASE);
      jobDeployment.setEnabled(true);
      jobDeployment.setResources(new DataJobResources());
      jobDeployment.setSchedule(new DataJobSchedule());
      jobDeployment.setId(deploymentId);

      return jobDeployment;
   }
}
