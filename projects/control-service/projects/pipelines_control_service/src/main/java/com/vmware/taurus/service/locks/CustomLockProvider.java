/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.locks;

import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.core.LockConfiguration;
import net.javacrumbs.shedlock.core.SimpleLock;
import net.javacrumbs.shedlock.provider.jdbctemplate.JdbcTemplateLockProvider;
import org.jetbrains.annotations.NotNull;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * A custom JdbcTemplateLockProvider that keeps track of all acquired and released locks, and can be
 * used on shutdown to release all locks that are still active.
 */
@Slf4j
class CustomLockProvider extends JdbcTemplateLockProvider {
  private final Map<String, SimpleLock> activeLocks = new ConcurrentHashMap<>();

  public CustomLockProvider(JdbcTemplate jdbcTemplate, String tableName) {
    super(jdbcTemplate, tableName);
  }

  @NotNull
  @Override
  public Optional<SimpleLock> lock(@NotNull LockConfiguration lockConfiguration) {
    var lock = super.lock(lockConfiguration);
    return lock.map(
        simpleLock -> new LockWrapper(simpleLock, lockConfiguration.getName(), activeLocks));
  }

  /** Attempts to release all active locks. */
  public void releaseActiveLocks() {
    if (activeLocks.size() > 0) {
      if (log.isInfoEnabled()) {
        var lockNames = activeLocks.keySet().stream().reduce((a, b) -> a + ", " + b).orElse("");
        log.info("Releasing {} active locks: {}", activeLocks.size(), lockNames);
      }
      activeLocks.values().forEach(SimpleLock::unlock);
    } else {
      log.info("There are no active locks to release");
    }
  }

  /**
   * A simple lock wrapper that tracks the lifetime of a lock. This class will probably not work if
   * using lock extension.
   */
  private static class LockWrapper implements SimpleLock {
    private final SimpleLock wrappedLock;
    private final String name;
    private final Map<String, SimpleLock> activeLocks;

    public LockWrapper(SimpleLock wrappedLock, String name, Map<String, SimpleLock> activeLocks) {
      log.debug("Acquiring lock {}", name);
      this.wrappedLock = wrappedLock;
      this.name = name;
      this.activeLocks = activeLocks;
      this.activeLocks.put(name, this);
      log.debug("Lock {} is acquired", name);
    }

    @Override
    public void unlock() {
      log.debug("Releasing lock {}", name);
      wrappedLock.unlock();
      activeLocks.remove(name);
      log.debug("Lock {} is released", name);
    }
  }
}
