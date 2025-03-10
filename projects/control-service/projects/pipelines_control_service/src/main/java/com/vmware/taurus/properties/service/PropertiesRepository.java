/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.properties.service;

import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PropertiesRepository extends CrudRepository<JobProperties, String> {

  Optional<JobProperties> findByJobName(String jobName);
}
