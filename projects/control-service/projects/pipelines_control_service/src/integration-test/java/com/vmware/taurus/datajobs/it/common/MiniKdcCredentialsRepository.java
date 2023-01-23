/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.vmware.taurus.service.credentials.KerberosCredentialsRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.File;
import java.util.Optional;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Component;

/**
 * This class can be used to replace {@link KerberosCredentialsRepository} for testing purposes. It
 * uses {@link SimpleKdcServer} as a kerberos server.
 *
 * <p>TODO: Figure out how to connect to a testing KDC server via kadmin * For some reason I
 * (tsvetkovt@vmware.com) was not able to connect to MiniKdc or to a * dockerized KDC with kadmin.
 * TODO we should think about moving away from MiniKDC as it's not maintained.
 */
@Component
@Primary
public class MiniKdcCredentialsRepository extends KerberosCredentialsRepository {
  private static final Logger log = LoggerFactory.getLogger(MiniKdcCredentialsRepository.class);

  private SimpleKdcServer miniKdc;

  @Autowired
  public MiniKdcCredentialsRepository(SimpleKdcServer miniKdc) {
    super("test", "test");
    this.miniKdc = miniKdc;
  }

  @Override
  public void createPrincipal(String principal, Optional<File> keytabLocation) {
    try {
      miniKdc.createAndExportPrincipals(keytabLocation.get(), principal);
    } catch (Exception e) {
      log.error("Failed to create principal", e);
    }
  }

  @Override
  public boolean principalExists(String principal) {
    return false;
  }

  @Override
  public void deletePrincipal(String principal) {
    // Principals are deleted when MiniKdc is shut down.
  }
}
