/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
package com.vmware.taurus.authorization;

import com.kerb4j.client.SpnegoClient;
import com.kerb4j.client.SpnegoContext;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import org.apache.kerby.kerberos.kerb.KrbException;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.apache.kerby.util.NetworkUtil;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.File;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * This test is in the unit tests directory, because
 * our integration tests use the MiniKdc server provided
 * by spring which as of today hasn't received any updates
 * in a long time and is problematic. However, minikdc leaves
 * some files and configurations that interfere with apache kerby
 * and both tests cannot run on the same runner (even after invoking
 * the provided cleanup mehtods by the libraries). We should look into
 * migrating to apache kerby for our integration tests too. This
 * test was deemed OK to be a unit test since it runs fast (2 seconds)
 * and doesn't rely on any external configurations or environments.
 */
@TestPropertySource(properties = {
      "test.dir=target",
      "featureflag.security.enabled=true",
      "datajobs.security.kerberos.enabled=true",
      "featureflag.authorization.enabled=false",
      "datajobs.security.kerberos.kerberosPrincipal=HTTP/localhost",
      "datajobs.security.kerberos.keytabFileLocation=target/foo.keytab",
      "datajobs.security.kerberos.krb5ConfigLocation=target/krb5.conf",
      "java.security.krb5.conf=target/krb5.conf",
      "sun.security.krb5.debug=true",
      "datajobs.authorization.authorized-roles="
})
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
@ExtendWith(SpringExtension.class)
public class KerberosAuthenticationIT {

   /*
    * Using static variables due to the KDC instance needing to init before
    * spring startup code from the @SpringBootTest annotation.
    */
   private static final String WORK_DIR = "target";
   private static final File KDC_WORK_DIR = new File(WORK_DIR);
   private static final File KEYTAB = new File(WORK_DIR + "/foo.keytab");
   private static final String CLIENT_PRINCIPAL = "client/localhost";
   private static final String TGT_PRINCIPAL = "HTTP/localhost";

   private static SimpleKdcServer simpleKdcServer;

   @Autowired
   private JobsRepository jobsRepository;

   private DataJob dataJob;

   @LocalServerPort
   int randomPort;

   /*
    * Static block is only reliable way of starting the KDC server before
    * code invoked by the @SpringBootTest annotation. If you find a way to
    * refactor this in a JUnit method such as @BeforeAll etc. feel free to.
    */
   static {
      // Initialize the KDC server
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
         System.out.println(e);
      }
   }

   @BeforeEach
   public void addTestJob() {
      // Add a dummy data job so that endpoint call returns 200 instead of 404
      dataJob = new DataJob();
      var config = new JobConfig();
      config.setTeam("test-team");
      dataJob.setName("test-name");
      dataJob.setJobConfig(config);
      jobsRepository.save(dataJob);
   }

   @Test
   public void testAuthenticatedCall() throws Exception {

      SpnegoClient spnegoClient = SpnegoClient.loginWithKeyTab(CLIENT_PRINCIPAL, KEYTAB.getPath());
      URL url = new URL("http://127.0.0.1:" + randomPort + "/data-jobs/for-team/test-team/jobs/test-name");
      var krb5 = simpleKdcServer.getKrbClient().getKrbConfig();
      SpnegoContext context = spnegoClient.createContext(new URL("http://" + krb5.getKdcHost() + "/" + krb5.getKdcPort()));
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      conn.setRequestProperty("Authorization", context.createTokenAsAuthroizationHeader());
      var res = conn.getResponseCode();

      Assertions.assertEquals(200, res);
   }

   @Test
   public void testUnauthenticatedCall() throws Exception {
      URL url = new URL("http://127.0.0.1:" + randomPort + "/data-jobs/for-team/test/jobs/test");
      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      var res = conn.getResponseCode();
      Assertions.assertEquals(401, res);
   }

   @AfterEach
   public void cleanupJob() {
      jobsRepository.delete(dataJob);
   }

   @AfterAll
   public static void cleanup() throws KrbException {
      KDC_WORK_DIR.deleteOnExit();
      simpleKdcServer.stop();
   }

}
