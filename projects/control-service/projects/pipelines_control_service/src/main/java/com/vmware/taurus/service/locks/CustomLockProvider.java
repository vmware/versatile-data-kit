/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.locks;

import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.core.LockConfiguration;
import net.javacrumbs.shedlock.core.SimpleLock;
import net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateLockProvider;
import net.javacrumbs.shedlock.support.annotation.NonNull;
import org.jetbrains.annotations.NotNull;

import javax.sql.DataSource;
import java.time.Duration;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A custom JdbcTemplateLockProvider that keeps track of all acquired and released locks,
 * and can be used on shutdown to release all locks that are still active.
 */
@Slf4j
class CustomLockProvider extends JdbcTemplateLockProvider {
    private final Map<String, SimpleLock> activeLocks = new ConcurrentHashMap<>();

    public CustomLockProvider(DataSource dataSource, String tableName) {
        super(dataSource, tableName);
    }

    @NotNull
    @Override
    public Optional<SimpleLock> lock(@NotNull LockConfiguration lockConfiguration) {
        var lock = super.lock(lockConfiguration);
        return lock.map(simpleLock -> new LockWrapper(simpleLock, lockConfiguration.getName(), activeLocks));
    }

    /**
     * Attempts to release all active locks.
     */
    public void releaseActiveLocks() {
        if (activeLocks.size() > 0) {
            if (log.isInfoEnabled()) {
                var lockNames = activeLocks.keySet().stream()
                        .reduce((a, b) -> a + b)
                        .orElse("");
                log.info("Releasing {} active locks: {}", activeLocks.size(), lockNames);
            }
            activeLocks.values().forEach(SimpleLock::unlock);
        }
    }

    /**
     * A simple lock wrapper that tracks the lifetime of a lock.
     * This class will probably not work if using lock extension.
     */
    private static class LockWrapper implements SimpleLock {
        private final SimpleLock wrappedLock;
        private final String name;
        private final Map<String, SimpleLock> activeLocks;

        public LockWrapper(SimpleLock wrappedLock, String name, Map<String, SimpleLock> activeLocks) {
            this.wrappedLock = wrappedLock;
            this.name = name;
            this.activeLocks = activeLocks;
            this.activeLocks.put(name, this);
            log.debug("Acquiring lock {}", name);
        }

        @Override
        public void unlock() {
            wrappedLock.unlock();
            activeLocks.remove(name);
            log.debug("Releasing lock {}", name);
        }
    }
}
