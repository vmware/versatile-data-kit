/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.service.upload.JobUpload;
import org.mockito.Mockito;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;

/**
 * Registers a bean with a non-functional mock mainly for {@link JobUpload}. The class can be used
 * to mock any Git related functionality.
 */
@Profile("MockGit")
@Configuration
public class MockGit {

  @Bean
  @Primary
  public JobUpload mockJobUpload() {
    JobUpload mock = mock(JobUpload.class);
    Mockito.doNothing().when(mock).deleteDataJob(any(), any());
    return mock;
  }
}
