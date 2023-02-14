/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import org.apache.commons.lang3.SystemUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.net.InetAddress;

@Service
public class UserAgentService {

  @Value("${datajobs.version:unknown-version}")
  private String dataJobsVersion;

  @Value("${datajobs.git_commit_hash:unknown-git-hash}")
  private String dataJobsGitCommit;

  public String getUserAgent() {
    return String.format("PipelinesControlService/%s", this.dataJobsVersion);
  }

  public String getUserAgentDetails() {
    return String.format(
        "PipelinesControlService/%s/%s (%s@%s %s)",
        this.dataJobsVersion,
        this.dataJobsGitCommit,
        SystemUtils.USER_NAME,
        getHostName(),
        getOsDetails());
  }

  private static String getOsDetails() {
    return String.format("%s/%s/%s", SystemUtils.OS_NAME, SystemUtils.OS_ARCH, SystemUtils.OS_ARCH);
  }

  private static String getHostName() {
    try {
      return InetAddress.getLocalHost().getHostName();
    } catch (Exception e) {
      return SystemUtils.getHostName();
    }
  }
}
