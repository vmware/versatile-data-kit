/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

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
@Transactional
@Repository
public interface DesiredJobDeploymentRepository
    extends JpaRepository<DesiredDataJobDeployment, String> {

  @Modifying
  @Query(
      "update DesiredDataJobDeployment d set d.enabled = :enabled where d.dataJobName ="
          + " :dataJobName")
  int updateDesiredDataJobDeploymentEnabledByDataJobName(
      @Param(value = "dataJobName") String dataJobName, @Param(value = "enabled") Boolean enabled);

  @Modifying
  @Query(
      "update DesiredDataJobDeployment d set d.status = :status, d.userInitiated = :userInitiated"
          + " where d.dataJobName = :dataJobName")
  int updateDesiredDataJobDeploymentStatusAndUserInitiatedByDataJobName(
      @Param(value = "dataJobName") String dataJobName,
      @Param(value = "status") DeploymentStatus status,
      @Param(value = "userInitiated") Boolean userInitiatedDeployment);
}
