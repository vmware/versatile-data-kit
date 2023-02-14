/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

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
import java.io.IOException;
import java.nio.file.Files;

/**
 * This class instantiates a test Kerberos server with a client and server principals which can be
 * used in testing to authorize requests.
 */
@Slf4j
public class TestKerberosServerHelper {

  private static final String WORK_DIR = "target";
  private static final File KDC_WORK_DIR = new File(WORK_DIR);
  private static final String TGT_PRINCIPAL = "HTTP/localhost";

  @Getter private static final File KEYTAB = new File(WORK_DIR + "/foo.keytab");
  @Getter private static final String CLIENT_PRINCIPAL = "client/localhost";
  @Getter private static SimpleKdcServer simpleKdcServer;

  /**
   * Using static block to initialize instead of constructor because this is the only reliable way
   * to have this code run before Spring boot test annotations. When using a constructor or JUnit
   * Extensions test classes annotated with the @SpringBootTest annotation that depend on an
   * initialized Kerberos server will fail.
   */
  static {
    try {
      Files.createDirectory(KDC_WORK_DIR.toPath());
    } catch (IOException e) {
      log.error("Failed to create test directory.", e);
    }

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
    } catch (Exception e) {
      log.error("Failed to initialize test server. Tests will likely fail.", e);
    }
  }

  public static void shutdownServer() throws KrbException, IOException {
    simpleKdcServer.stop();
    Files.delete(KEYTAB.toPath());
    try {
      Files.delete(KDC_WORK_DIR.toPath());
    } catch (Exception e) {
      // This error happens occasionally when running tests locally. It is no real concern that the
      // dir is not cleaned up.
      log.error("Failed to delete test directory.", e);
    }
  }
}
