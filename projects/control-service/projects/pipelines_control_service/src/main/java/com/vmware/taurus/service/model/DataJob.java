/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;
import java.time.OffsetDateTime;
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
   @Convert(converter = ExecutionTerminationStatusConverter.class)
   private ExecutionTerminationStatus latestJobTerminationStatus;

   @Column(name = "latest_job_execution_id")
   private String latestJobExecutionId;

   @OneToMany(
         mappedBy = "dataJob",
         cascade = CascadeType.ALL
   )
   @ToString.Exclude
   @EqualsAndHashCode.Exclude
   private Set<DataJobExecution> executions;

   private Boolean enabled;

   @Column(name = "last_execution_status")
   private ExecutionStatus lastExecutionStatus;

   @Column(name = "last_execution_end_time")
   private OffsetDateTime lastExecutionEndTime;

   @Column(name = "last_execution_duration")
   private Integer lastExecutionDuration;

   public DataJob(String name, JobConfig jobConfig) {
      this.name = name;
      this.jobConfig = jobConfig;
      this.latestJobDeploymentStatus = DeploymentStatus.NONE;
      this.latestJobTerminationStatus = ExecutionTerminationStatus.NONE;
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus) {
      this(name, jobConfig, deploymentStatus, ExecutionTerminationStatus.NONE, null, null, true, null, null, null);
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus, ExecutionTerminationStatus terminationStatus, String latestJobExecutionId) {
      this(name, jobConfig, deploymentStatus, terminationStatus, latestJobExecutionId, null, true, null, null, null);
   }
}
