/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import com.vmware.taurus.service.credentials.KerberosCredentialsRepository;
import lombok.Setter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.kerberos.test.MiniKdc;

import java.io.File;
import java.util.Optional;

/**
 * This class can be used to replace {@link KerberosCredentialsRepository} for testing purposes.
 * It uses {@link MiniKdc} as a kerberos server.
 *
 * TODO: Figure out how to connect to a testing KDC server via kadmin
 ** For some reason I (tsvetkovt@vmware.com) was not able to connect to MiniKdc or to a
 ** dockerized KDC with kadmin.
 */
@Setter
public class MiniKdcCredentialsRepository extends KerberosCredentialsRepository {
   private static final Logger log = LoggerFactory.getLogger(MiniKdcCredentialsRepository.class);

   private MiniKdc miniKdc;

   public MiniKdcCredentialsRepository() {
      super("test", "test");
   }

   @Override
   public void createPrincipal(String principal, Optional<File> keytabLocation) {
      try {
         miniKdc.createPrincipal(keytabLocation.get(), principal);
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
