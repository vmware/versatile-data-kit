/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;
import java.time.OffsetDateTime;

import com.vmware.taurus.service.model.converter.ExecutionStatusConverter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
@ToString
@Builder(toBuilder=true)
@Entity
public class DataJobExecution {

   @Id
   private String id;

   @ManyToOne
   @JoinColumn(name = "job_name", nullable = false)
   @ToString.Exclude
   @EqualsAndHashCode.Exclude
   private DataJob dataJob;

   @Column(nullable = false)
   private ExecutionType type;

   @Column(nullable = false)
   @Convert(converter = ExecutionStatusConverter.class)
   private ExecutionStatus status;

   private String message;

   @Column(nullable = false)
   private String opId;

   private OffsetDateTime startTime;

   private OffsetDateTime endTime;

   private String vdkVersion;

   private String jobVersion;

   private String jobSchedule;

   private Float resourcesCpuRequest;

   private Float resourcesCpuLimit;

   private Integer resourcesMemoryRequest;

   private Integer resourcesMemoryLimit;

   private OffsetDateTime lastDeployedDate;

   private String lastDeployedBy;

   private String startedBy;
}
