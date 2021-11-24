/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;

import com.vmware.taurus.ControlplaneApplication;

/**
 * It combines all necessary annotations and constants
 * for tests that need an already deployed data job.
 *
 * The test just needs to extend this class,
 * and it will have access to the already deployed data job.
 */
@Import({BaseDataJobDeploymentIT.TaskExecutorConfig.class})
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
@ExtendWith(DataJobDeploymentExtension.class)
public abstract class BaseDataJobDeploymentIT extends BaseIT {

   @TestConfiguration
   public static class TaskExecutorConfig {
      @Bean
      @Primary
      public TaskExecutor taskExecutor() {
         // Deployment methods are non-blocking (Async) which makes them harder to test.
         // Making them sync for the purposes of this test.
         return new SyncTaskExecutor();
      }
   }
}
