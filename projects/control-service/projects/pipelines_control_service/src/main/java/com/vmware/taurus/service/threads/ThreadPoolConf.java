/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.threads;

import com.vmware.taurus.service.monitoring.DataJobMonitorSync;
import com.vmware.taurus.service.monitoring.DeploymentMonitorSync;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;

/**
 * This class configures thread pool which which is used in all methods which have Async annotation.
 *
 * <p>TODO: every class which has asynchronous methods should have dedicated thread executor instead
 * of having generic thread pool for all asynchronous methods
 */
@EnableAsync
@Configuration
public class ThreadPoolConf {

  @Value("${datajobs.deployment.configuration.synchronization.task.corePoolSize}")
  private int synchronizationTaskCorePoolSize;

  @Value("${datajobs.deployment.configuration.synchronization.task.maxPoolSize}")
  private int synchronizationTaskMaxPoolSize;

  @Value("${datajobs.deployment.configuration.synchronization.task.queueCapacity}")
  private int synchronizationTaskQueueCapacity;

  @Value("${datajobs.deployment.configuration.synchronization.task.keepAliveSeconds}")
  private int synchronizationTaskKeepAliveSeconds;

  /**
   * This method configures the max number of scheduled threads which for now is one as we only use
   * it in a single place
   *
   * @see DeploymentMonitorSync
   * @see DataJobMonitorSync
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

  @Bean(name = "dataJobsSynchronizerTaskExecutor")
  public ThreadPoolTaskExecutor dataJobsSynchronizerTaskExecutor() {
    ThreadPoolTaskExecutor taskExecutor = new ThreadPoolTaskExecutor();
    taskExecutor.setCorePoolSize(synchronizationTaskCorePoolSize);
    taskExecutor.setMaxPoolSize(synchronizationTaskMaxPoolSize);
    taskExecutor.setQueueCapacity(synchronizationTaskQueueCapacity);
    taskExecutor.setAllowCoreThreadTimeOut(true);
    taskExecutor.setKeepAliveSeconds(synchronizationTaskKeepAliveSeconds);
    taskExecutor.setWaitForTasksToCompleteOnShutdown(true);
    taskExecutor.initialize();

    return taskExecutor;
  }
}
