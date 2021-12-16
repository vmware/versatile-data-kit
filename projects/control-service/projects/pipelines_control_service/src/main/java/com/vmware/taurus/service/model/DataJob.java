/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;
import java.time.OffsetDateTime;
import java.util.Set;

import com.vmware.taurus.service.model.converter.ExecutionStatusConverter;
import com.vmware.taurus.service.model.converter.ExecutionTerminationStatusConverter;

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
   private ExecutionStatus latestJobTerminationStatus;

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
   @Convert(converter = ExecutionStatusConverter.class)
   private ExecutionStatus lastExecutionStatus;

   @Column(name = "last_execution_end_time")
   private OffsetDateTime lastExecutionEndTime;

   @Column(name = "last_execution_duration")
   private Integer lastExecutionDuration;

   public DataJob(String name, JobConfig jobConfig) {
      this.name = name;
      this.jobConfig = jobConfig;
      this.latestJobDeploymentStatus = DeploymentStatus.NONE;
      this.latestJobTerminationStatus = null;
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus) {
      this(name, jobConfig, deploymentStatus, null, null, null, true, null, null, null);
   }

   public DataJob(String name, JobConfig jobConfig, DeploymentStatus deploymentStatus, ExecutionStatus terminationStatus, String latestJobExecutionId) {
      this(name, jobConfig, deploymentStatus, terminationStatus, latestJobExecutionId, null, true, null, null, null);
   }
}
