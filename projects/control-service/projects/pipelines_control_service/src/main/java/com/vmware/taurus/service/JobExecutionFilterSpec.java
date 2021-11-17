/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaQuery;
import javax.persistence.criteria.Predicate;
import javax.persistence.criteria.Root;
import java.util.ArrayList;
import java.util.List;

import lombok.AllArgsConstructor;
import org.apache.commons.collections.CollectionUtils;
import org.springframework.data.jpa.domain.Specification;

import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.DataJobExecution_;

@AllArgsConstructor
public class JobExecutionFilterSpec implements Specification<DataJobExecution> {

   private DataJobExecutionFilter filter;

   @Override
   public Predicate toPredicate(Root<DataJobExecution> root, CriteriaQuery<?> query, CriteriaBuilder builder) {
      List<Predicate> predicates = new ArrayList<>();

      if (filter != null) {
         if (filter.getStartTimeGte() != null) {
            predicates.add(builder.greaterThanOrEqualTo(root.get(DataJobExecution_.START_TIME), filter.getStartTimeGte()));
         }

         if (filter.getEndTimeGte() != null) {
            predicates.add(builder.greaterThanOrEqualTo(root.get(DataJobExecution_.END_TIME), filter.getEndTimeGte()));
         }

         if (CollectionUtils.isNotEmpty(filter.getStatusIn())) {
            predicates.add(root.get(DataJobExecution_.STATUS).in(filter.getStatusIn()));
         }
      }

      return builder.and(predicates.toArray(new Predicate[0]));
   }
}
