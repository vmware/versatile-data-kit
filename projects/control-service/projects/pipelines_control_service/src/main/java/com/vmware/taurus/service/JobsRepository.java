/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.model.DataJob;
import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.stereotype.Repository;

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

   boolean existsDataJobByNameAndJobConfigTeam(String jobName, String teamName);
}
