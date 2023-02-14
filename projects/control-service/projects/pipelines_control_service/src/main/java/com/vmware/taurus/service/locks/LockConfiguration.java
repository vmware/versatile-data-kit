/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.locks;

import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.core.LockProvider;
import net.javacrumbs.shedlock.spring.annotation.EnableSchedulerLock;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;

import javax.annotation.PreDestroy;
import javax.sql.DataSource;

@EnableScheduling
@EnableSchedulerLock(defaultLockAtMostFor = "10m")
@Configuration
@Slf4j
public class LockConfiguration {

  /**
   * We have experienced cases when operations against the database appear to hang indefinitely
   * (usually after a connectivity issue with the database). As a result tasks that attempt to
   * obtain a distributed lock, fail to start. This value is set directly on the JdbcTemplate as a
   * query timeout in an attempt to force the database operation to time out and prevent such cases.
   *
   * @see <a href="https://dzone.com/articles/threads-stuck-in-javanetsocketinputstreamsocketrea">
   *     Threads Stuck in java.net.SocketInputStream.socketRead0 API</a>
   */
  private static final int LOCK_PROVIDER_QUERY_TIMEOUT_SECONDS = 60;

  private CustomLockProvider customLockProvider;

  /**
   * Creates an object that is used by the ShedLock utility to connect to a database.
   *
   * <p>The ShedLock utility ensures that a scheduled task (data job status monitoring in our case)
   * can only occur in one of the service instances (in case of a multi-instance service
   * deployment). This is achieved by using a database table and the LockProvider returned by this
   * method is used to connect to that table.
   *
   * @see <a href="https://github.com/lukas-krecan/ShedLock">ShedLock</a>
   */
  @Bean
  public LockProvider lockProvider(DataSource dataSource) {
    JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);
    jdbcTemplate.setQueryTimeout(LOCK_PROVIDER_QUERY_TIMEOUT_SECONDS);
    customLockProvider = new CustomLockProvider(jdbcTemplate, "shedlock");
    return customLockProvider;
  }

  @PreDestroy
  void releaseActiveLocks() {
    log.info("Service is shutting down. Releasing active locks...");
    if (customLockProvider != null) {
      customLockProvider.releaseActiveLocks();
    }
  }
}
