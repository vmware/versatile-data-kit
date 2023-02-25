/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

/**
 * TODO: enable it in CICD: apk --no-cache add krb5 + pointing to the krb5.conf + using
 * hadoop-minikdc or docker KDC server
 */
public class KerberosCredentialsServiceTestManual {

  @Test
  public void test() throws IOException {
    String kadminUser = System.getProperty("kadmin_password", "phuser/admin");
    String kadminPassword = System.getProperty("kadmin_password");

    Assumptions.assumeTrue(
        kadminPassword != null && !kadminPassword.isBlank(),
        "kadmin_password is missing. Assuming test is disabled.");

    KerberosCredentialsRepository service =
        new KerberosCredentialsRepository(kadminUser, kadminPassword);

    File file = File.createTempFile("keytab_test", ".keytab");
    file.deleteOnExit();

    String principal = "taurus-pipelines-test-user";
    service.deletePrincipal(principal);
    Assertions.assertFalse(service.principalExists(principal));
    service.createPrincipal(principal, Optional.of(file));
    Assertions.assertTrue(service.principalExists(principal));
    Assertions.assertTrue(file.exists());
    Assertions.assertTrue(file.length() > 0);
    service.deletePrincipal(principal);
    Assertions.assertFalse(service.principalExists(principal));
  }
}
