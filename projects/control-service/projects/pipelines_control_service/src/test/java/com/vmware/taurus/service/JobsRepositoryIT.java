/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

/**
 * Integration tests of the setup of Spring Data repository for data jobs
 */
@RunWith(SpringRunner.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobsRepositoryIT {

   @Autowired
   private JobsRepository repository;

   @Before
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
      var entity = new DataJob("hello", config, DeploymentStatus.NONE);
      var savedEntity = repository.save(entity);
      Assert.assertEquals(entity, savedEntity);

      Iterable<DataJob> jobs = repository.findAll();
      Assert.assertEquals(entity, jobs.iterator().next());
      Assert.assertEquals(entity.getJobConfig(), jobs.iterator().next().getJobConfig());
   }

   @Test
   public void testEmptyJobConfigIsReadAsNull() {
      var entity = new DataJob("hello", new JobConfig(), DeploymentStatus.NONE);
      entity = repository.save(entity);
      Assert.assertNotNull(entity.getJobConfig());
      entity = repository.findById("hello").get();
      var expectedJobConfig = new JobConfig(null, null, null, null, null, null, null, null, null, null, false, null);
      Assert.assertEquals(entity.getJobConfig(), expectedJobConfig);

      Assert.assertEquals(entity.getLatestJobDeploymentStatus(), DeploymentStatus.NONE);
   }
}
