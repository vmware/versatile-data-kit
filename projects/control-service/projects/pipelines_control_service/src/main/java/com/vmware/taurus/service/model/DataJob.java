/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;
import java.util.Set;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Entity
public class DataJob {

   @Id
   private String name;

   @Embedded
   private JobConfig jobConfig;

   @Column(name = "latest_job_deployment_status")
   private DeploymentStatus latestJobDeploymentStatus;

   @Column(name = "latest_job_termination_status")
   private TerminationStatus latestJobTerminationStatus;

   @Column(name = "latest_job_execution_id")
   private String latestJobExecutionId;

   @OneToMany(
         mappedBy = "dataJob",
         cascade = CascadeType.ALL
   )
   @ToString.Exclude
   @EqualsAndHashCode.Exclude
   private Set<DataJobExecution> executions;

   public DataJob(String name, JobConfig jobConfig) {
      this.name = name;
      this.jobConfig = jobConfig;
      this.latestJobDeploymentStatus = DeploymentStatus.NONE;
      this.latestJobTerminationStatus = TerminationStatus.NONE;
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus) {
      this(name, jobConfig, deploymentStatus, TerminationStatus.NONE, null, null);
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus, TerminationStatus terminationStatus, String latestJobExecutionId) {
      this(name, jobConfig, deploymentStatus, terminationStatus, latestJobExecutionId, null);
   }
}
