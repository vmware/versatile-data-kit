/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.service.model.ActualDataJobDeployment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/**
 * Spring Data / JPA Repository for ActualDataJobDeployment objects and their members
 *
 * <p>Spring Data automatically creates an implementation of this interface at runtime, provided
 * {@link ActualDataJobDeployment} is a valid JPA entity.
 *
 * <p>Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing
 * to the database.
 *
 * <p>JobDeploymentRepositoryIT validates some aspects of the behavior
 */
@Transactional
@Repository
public interface ActualJobDeploymentRepository
    extends JpaRepository<ActualDataJobDeployment, String> {}
