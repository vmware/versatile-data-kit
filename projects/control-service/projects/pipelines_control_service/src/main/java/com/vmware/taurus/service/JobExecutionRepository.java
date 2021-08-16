/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.DataJobExecutionIdAndEndTime;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

/**
 * Spring Data / JPA Repository for DataJobExecution objects and their members
 *
 * <p>
 * Spring Data automatically creates an implementation of this interface at runtime, provided {@link DataJobExecution}
 * is a valid JPA entity.
 *
 * <p>
 * Methods throw {@link org.springframework.dao.DataAccessException} in case of issues of writing to the database.
 *
 * <p>
 * JobExecutionRepositoryIT validates some aspects of the behavior
 */
public interface JobExecutionRepository extends JpaRepository<DataJobExecution, String> {

   List<DataJobExecution> findDataJobExecutionsByDataJobName(String jobName);

   List<DataJobExecution> findDataJobExecutionsByDataJobNameAndStatusIn(String jobName, List<ExecutionStatus> statuses);

   List<DataJobExecutionIdAndEndTime> findByDataJobNameAndStatusNotInOrderByEndTime(String jobName, List<ExecutionStatus> statuses);

   List<DataJobExecution> findFirst5ByDataJobNameOrderByStartTimeDesc(String jobName);

}
