/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.ExecutionTerminationStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Integration tests of the setup of Spring Data repository for data jobs
 */
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobsRepositoryIT {

   @Autowired
   private JobsRepository repository;

   @BeforeEach
   public void setUp() throws Exception {
      repository.deleteAll();
   }

   /**
    * Confirms that writing and reading jobs also covers their configuration and keeps equality overall
    */
   @Test
   public void testLoadEmbedded() {
      JobConfig config = new JobConfig();
      config.setSchedule("schedule");
      var entity = new DataJob("hello", config, DeploymentStatus.NONE, ExecutionTerminationStatus.USER_ERROR, "1234");
      var savedEntity = repository.save(entity);
      Assertions.assertEquals(entity, savedEntity);

      Iterable<DataJob> jobs = repository.findAll();
      Assertions.assertEquals(entity, jobs.iterator().next());
      Assertions.assertEquals(entity.getJobConfig(), jobs.iterator().next().getJobConfig());
   }

   @Test
   public void testEmptyJobConfigIsReadAsNull() {
      var entity = new DataJob("hello", new JobConfig(), DeploymentStatus.NONE);
      entity = repository.save(entity);
      Assertions.assertNotNull(entity.getJobConfig());
      entity = repository.findById("hello").get();
      var expectedJobConfig = new JobConfig(null, null, null, null, null, null, null, null, null, null, false, null);
      Assertions.assertEquals(entity.getJobConfig(), expectedJobConfig);

      Assertions.assertEquals(entity.getLatestJobDeploymentStatus(), DeploymentStatus.NONE);
   }
}
