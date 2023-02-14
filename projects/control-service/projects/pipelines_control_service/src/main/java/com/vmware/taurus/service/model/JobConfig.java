/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import javax.persistence.Column;
import javax.persistence.Embeddable;
import java.util.List;

import static com.vmware.taurus.service.Utilities.join;
import static com.vmware.taurus.service.Utilities.parseList;

@Getter
@Setter
@NoArgsConstructor
@EqualsAndHashCode
@ToString
@Embeddable
@AllArgsConstructor
public class JobConfig {

  private static final String SEPARATOR = ";";
  private String team;
  private String description;
  private String schedule;

  // JPA/Hibernate automatically converts camelCase field names to snake_case column names
  private String dbDefaultType;
  private Boolean enableExecutionNotifications;
  private Integer notificationDelayPeriodMinutes;
  private String notifiedOnJobFailureUserError;
  private String notifiedOnJobFailurePlatformError;
  private String notifiedOnJobSuccess;
  private String notifiedOnJobDeploy;
  private boolean generateKeytab;

  @Column(name = "name_deprecated")
  private String jobName;

  public List<String> getNotifiedOnJobFailureUserError() {
    return parseList(notifiedOnJobFailureUserError);
  }

  public void setNotifiedOnJobFailureUserError(List<String> list) {
    this.notifiedOnJobFailureUserError = join(list);
  }

  public List<String> getNotifiedOnJobFailurePlatformError() {
    return parseList(notifiedOnJobFailurePlatformError);
  }

  public void setNotifiedOnJobFailurePlatformError(List<String> list) {
    this.notifiedOnJobFailurePlatformError = join(list);
  }

  public List<String> getNotifiedOnJobSuccess() {
    return parseList(notifiedOnJobSuccess);
  }

  public void setNotifiedOnJobSuccess(List<String> list) {
    this.notifiedOnJobSuccess = join(list);
  }

  public List<String> getNotifiedOnJobDeploy() {
    return parseList(notifiedOnJobDeploy);
  }

  public void setNotifiedOnJobDeploy(List<String> list) {
    this.notifiedOnJobDeploy = join(list);
  }
}
