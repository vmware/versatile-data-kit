/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization;

import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.apache.kerby.kerberos.kerb.KrbException;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.apache.kerby.util.NetworkUtil;

import java.io.File;

/**
 *  This class instantiates a test Kerberos server with a
 *  client and server principals which can be used in testing
 *  to authorize requests.
 */
@Getter
@Slf4j
public class TestKerberosServer {

   private final String WORK_DIR = "target";
   private final File KDC_WORK_DIR = new File(WORK_DIR);
   private final File KEYTAB = new File(WORK_DIR + "/foo.keytab");
   private final String CLIENT_PRINCIPAL = "client/localhost";
   private final String TGT_PRINCIPAL = "HTTP/localhost";

   private SimpleKdcServer simpleKdcServer;

   public TestKerberosServer() {
      try {
         simpleKdcServer = new SimpleKdcServer();
         simpleKdcServer.setWorkDir(KDC_WORK_DIR);
         simpleKdcServer.setAllowTcp(true);
         simpleKdcServer.setAllowUdp(true);
         simpleKdcServer.setKdcUdpPort(NetworkUtil.getServerPort());
         // Start the KDC server
         simpleKdcServer.init();
         simpleKdcServer.start();
         simpleKdcServer.createAndExportPrincipals(KEYTAB, CLIENT_PRINCIPAL, TGT_PRINCIPAL);
      } catch (KrbException e) {
         log.error("Failed to initialize test server. Tests will likely fail.");
      }
   }

   public void shutdownServer() throws KrbException {
      KDC_WORK_DIR.deleteOnExit();
      simpleKdcServer.stop();
   }
}
