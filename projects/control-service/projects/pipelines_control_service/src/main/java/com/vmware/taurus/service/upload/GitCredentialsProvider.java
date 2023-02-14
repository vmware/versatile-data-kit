/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.eclipse.jgit.transport.CredentialsProvider;
import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Class responsible for handling different credential providers.
 *
 * <p>Currently the implementation is using access token the way GitLab authentication expects it.
 * Other providers are explained: https://www.codeaffine.com/2014/12/09/jgit-authentication/
 */
@Component
public class GitCredentialsProvider {

  @Value("${datajobs.git.read.write.username:}")
  private String gitReadWriteUsername;

  @Value("${datajobs.git.read.write.password:}")
  private String gitReadWritePassword;

  public CredentialsProvider getProvider() {
    return new UsernamePasswordCredentialsProvider(gitReadWriteUsername, gitReadWritePassword);
  }
}
