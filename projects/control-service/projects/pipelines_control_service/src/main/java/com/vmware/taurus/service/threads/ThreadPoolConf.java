/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.threads;

import com.vmware.taurus.service.monitoring.DataJobMonitorSync;
import com.vmware.taurus.service.monitoring.DeploymentMonitorSync;
import net.javacrumbs.shedlock.core.LockProvider;
import net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateLockProvider;
import net.javacrumbs.shedlock.spring.annotation.EnableSchedulerLock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;

import javax.sql.DataSource;


/**
 * This class configures thread pool which which is used in all methods
 * which have Async annotation.
 *
 * TODO: every class which has asynchronous methods should have dedicated thread
 *  executor instead of having generic thread pool for all asynchronous methods
 */
@EnableScheduling
@EnableSchedulerLock(defaultLockAtMostFor = "10m")
@EnableAsync
@Configuration
public class ThreadPoolConf {

   /**
    * This method configures the max number of scheduled threads which for
    * now is one as we only use it in a single place
    *
    * @see DeploymentMonitorSync
    * @see DataJobMonitorSync
    *
    * @return
    */
   @Bean()
   public ThreadPoolTaskScheduler taskScheduler() {
      ThreadPoolTaskScheduler taskScheduler = new ThreadPoolTaskScheduler();
      taskScheduler.setPoolSize(6);
      taskScheduler.setThreadNamePrefix("thread-");
      taskScheduler.initialize();
      return taskScheduler;
   }

   /**
    * Creates an object that is used by the ShedLock utility to connect to
    * a database.
    * <p>
    * The ShedLock utility ensures that a scheduled task (data job status
    * monitoring in our case) can only occur in one of the service instances
    * (in case of a multi-instance service deployment). This is achieved
    * by using a database table and the LockProvider returned by this method
    * is used to connect to that table.
    *
    * @see   <a href="https://github.com/lukas-krecan/ShedLock">ShedLock</a>
    */
   @Bean
   public LockProvider lockProvider(DataSource dataSource) {
      return new JdbcTemplateLockProvider(dataSource, "shedlock");
   }
}
