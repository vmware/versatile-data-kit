/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.eclipse.jgit.transport.CredentialsProvider;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

public class GitCredentialsProviderTest {

  @Test
  public void testProperCredentials() {
    GitCredentialsProvider credentialsProvider = new GitCredentialsProvider();
    ReflectionTestUtils.setField(credentialsProvider, "gitReadWriteUsername", "example_user");
    ReflectionTestUtils.setField(credentialsProvider, "gitReadWritePassword", "z7d766asdv6019cz0a");

    CredentialsProvider provider = credentialsProvider.getProvider();
    Assertions.assertNotNull(provider);
  }

  @Test
  public void testEmptyCredentials() {
    GitCredentialsProvider credentialsProvider = new GitCredentialsProvider();
    ReflectionTestUtils.setField(credentialsProvider, "gitReadWriteUsername", "");
    ReflectionTestUtils.setField(credentialsProvider, "gitReadWritePassword", "");
    CredentialsProvider provider = credentialsProvider.getProvider();
    Assertions.assertNotNull(provider);
  }
}
