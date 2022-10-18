/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.model.*;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import javax.transaction.Transactional;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data / JPA Repository for DataJobExecution objects and their members
 *
 * <p>Spring Data automatically creates an implementation of this interface at runtime, provided
 * {@link DataJobExecution} is a valid JPA entity.
 *
 * <p>Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing
 * to the database.
 *
 * <p>JobExecutionRepositoryIT validates some aspects of the behavior
 */
public interface JobExecutionRepository
    extends JpaRepository<DataJobExecution, String>, JpaSpecificationExecutor<DataJobExecution> {

  List<DataJobExecution> findDataJobExecutionsByDataJobName(String jobName);

  Optional<DataJobExecution> findFirstByDataJobNameOrderByStartTimeDesc(String jobName);

  List<DataJobExecution> findDataJobExecutionsByDataJobName(String jobName, Pageable pageable);

  List<DataJobExecution> findDataJobExecutionsByDataJobNameAndStatusIn(
      String jobName, List<ExecutionStatus> statuses);

  List<DataJobExecutionIdAndEndTime> findByDataJobNameAndStatusNotInOrderByEndTime(
      String jobName, List<ExecutionStatus> statuses);

  List<DataJobExecution> findDataJobExecutionsByStatusInAndStartTimeBefore(
      List<ExecutionStatus> statuses, OffsetDateTime startTime);

  @Transactional
  void deleteDataJobExecutionByIdAndDataJobAndStatusAndType(
      String id, DataJob dataJob, ExecutionStatus status, ExecutionType type);

  @Query(
      "SELECT dje.status AS status, dje.dataJob.name AS jobName, count(dje.status) AS statusCount "
          + "FROM DataJobExecution dje "
          + "WHERE dje.status IN :statuses "
          + "AND dje.dataJob.name IN :dataJobs "
          + "GROUP BY dje.status, dje.dataJob")
  List<DataJobExecutionStatusCount> countDataJobExecutionStatuses(
      @Param("statuses") List<ExecutionStatus> statuses, @Param("dataJobs") List<String> dataJobs);

  @Query(
      "SELECT dje from DataJobExecution dje "
          + "LEFT JOIN DataJob dj ON dje.dataJob = dj.name "
          + "WHERE dje.id = :jobExecutionId "
          + "AND dj.name = :jobName "
          + "AND dj.jobConfig.team = :jobTeam")
  Optional<DataJobExecution> findDataJobExecutionByIdAndTeamAndName(
      String jobExecutionId, String jobName, String jobTeam);
}
