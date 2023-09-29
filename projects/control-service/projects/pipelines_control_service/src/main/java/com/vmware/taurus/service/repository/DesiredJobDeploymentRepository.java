/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Spring Data / JPA Repository for DesiredDataJobDeployment objects and their members
 *
 * <p>Spring Data automatically creates an implementation of this interface at runtime, provided
 * {@link DesiredDataJobDeployment} is a valid JPA entity.
 *
 * <p>Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing
 * to the database.
 *
 * <p>JobDeploymentRepositoryIT validates some aspects of the behavior
 */
@Repository
public interface DesiredJobDeploymentRepository extends JpaRepository<DesiredDataJobDeployment, String> {
}
