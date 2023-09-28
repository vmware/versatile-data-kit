/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import javax.transaction.Transactional;

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
public interface DesiredJobDeploymentRepository
    extends JpaRepository<DesiredDataJobDeployment, String> {

    @Transactional
    @Modifying(clearAutomatically = true)
    @Query("update DesiredDataJobDeployment d set d.enabled = :enabled where d.dataJobName = :dataJobName")
    int updateDesiredDataJobDeploymentEnabledByDataJobName(
            @Param(value = "dataJobName") String dataJobName, @Param(value = "enabled") Boolean enabled);
}
