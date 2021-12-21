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
import org.springframework.scheduling.annotation.EnableScheduling;

import javax.annotation.PreDestroy;
import javax.sql.DataSource;

@EnableScheduling
@EnableSchedulerLock(defaultLockAtMostFor = "10m")
@Configuration
@Slf4j
public class LockConfiguration {

    private CustomLockProvider customLockProvider;

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
        customLockProvider = new CustomLockProvider(dataSource, "shedlock");
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
