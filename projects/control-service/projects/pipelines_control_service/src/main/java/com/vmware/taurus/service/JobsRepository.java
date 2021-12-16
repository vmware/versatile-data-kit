/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import javax.transaction.Transactional;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data / JPA Repository for DataJob objects and their members
 *
 * <p>
 * Spring Data automatically creates an implementation of this interface at runtime, provided {@link DataJob}
 * is a valid JPA entity.
 *
 * <p>
 * Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing to the database.
 *
 * <p>
 * JobsRepositoryIT validates some aspects of the behavior
 */
@Repository
public interface JobsRepository extends PagingAndSortingRepository<DataJob, String> {
   List<DataJob> findAllByJobConfigTeam(String team, Pageable pageable);

   Optional<DataJob> findDataJobByNameAndJobConfigTeam(String jobName, String teamName);

    @Transactional
    @Modifying(clearAutomatically = true)
    @Query("update DataJob j set j.latestJobDeploymentStatus = :latestJobDeploymentStatus where j.name = :name")
    int updateDataJobLatestJobDeploymentStatusByName(
            @Param(value = "name") String name,
            @Param(value = "latestJobDeploymentStatus") DeploymentStatus latestJobDeploymentStatus);

    @Transactional
    @Modifying(clearAutomatically = true)
    @Query("update DataJob j set j.enabled = :enabled where j.name = :name")
    int updateDataJobEnabledByName(
            @Param(value = "name") String name,
            @Param(value = "enabled") Boolean enabled);

    @Transactional
    @Modifying(clearAutomatically = true)
    @Query("update DataJob j set j.lastExecutionStatus = :status, j.lastExecutionEndTime = :endTime, j.lastExecutionDuration = :duration where j.name = :name")
    int updateDataJobLastExecutionByName(
            @Param(value = "name") String name,
            @Param(value = "status") ExecutionStatus status,
            @Param(value = "endTime") OffsetDateTime endTime,
            @Param(value = "duration") Integer duration);

    @Transactional
    @Modifying(clearAutomatically = true)
    @Query("update DataJob j set j.latestJobTerminationStatus = :status, j.latestJobExecutionId = :id where j.name = :name")
    int updateDataJobLatestTerminationStatusByName(
            @Param(value = "name") String name,
            @Param(value = "status") ExecutionStatus status,
            @Param(value = "id") String id
    );

   boolean existsDataJobByNameAndJobConfigTeam(String jobName, String teamName);
}
