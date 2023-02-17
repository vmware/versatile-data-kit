/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.DataJobExecution_;
import com.vmware.taurus.service.model.DataJob_;
import com.vmware.taurus.service.model.JobConfig_;
import lombok.AllArgsConstructor;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.data.jpa.domain.Specification;

import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaQuery;
import javax.persistence.criteria.Predicate;
import javax.persistence.criteria.Root;
import java.util.ArrayList;
import java.util.List;

@AllArgsConstructor
public class JobExecutionFilterSpec implements Specification<DataJobExecution> {

  private DataJobExecutionFilter filter;

  @Override
  public Predicate toPredicate(
      Root<DataJobExecution> root, CriteriaQuery<?> query, CriteriaBuilder builder) {
    List<Predicate> predicates = new ArrayList<>();

    if (filter != null) {
      if (filter.getStartTimeGte() != null) {
        predicates.add(
            builder.greaterThanOrEqualTo(
                root.get(DataJobExecution_.START_TIME), filter.getStartTimeGte()));
      }

      if (filter.getStartTimeLte() != null) {
        predicates.add(
            builder.lessThanOrEqualTo(
                root.get(DataJobExecution_.START_TIME), filter.getStartTimeLte()));
      }

      if (filter.getEndTimeGte() != null) {
        predicates.add(
            builder.greaterThanOrEqualTo(
                root.get(DataJobExecution_.END_TIME), filter.getEndTimeGte()));
      }

      if (filter.getEndTimeLte() != null) {
        predicates.add(
            builder.lessThanOrEqualTo(
                root.get(DataJobExecution_.END_TIME), filter.getEndTimeLte()));
      }

      if (CollectionUtils.isNotEmpty(filter.getStatusIn())) {
        predicates.add(root.get(DataJobExecution_.STATUS).in(filter.getStatusIn()));
      }

      if (CollectionUtils.isNotEmpty(filter.getJobNameIn())) {
        predicates.add(
            root.get(DataJobExecution_.DATA_JOB).get(DataJob_.NAME).in(filter.getJobNameIn()));
      }

      if (CollectionUtils.isNotEmpty(filter.getTeamNameIn())) {
        predicates.add(
            root.get(DataJobExecution_.DATA_JOB)
                .get(DataJob_.JOB_CONFIG)
                .get(JobConfig_.TEAM)
                .in(filter.getTeamNameIn()));
      }
    }

    return builder.and(predicates.toArray(new Predicate[0]));
  }
}
