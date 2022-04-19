/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */
package com.vmware.taurus.datajobs.it;

import com.kerb4j.client.SpnegoClient;
import com.kerb4j.client.SpnegoContext;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.JobsRepository;
import org.apache.kerby.kerberos.kerb.KrbException;
import org.apache.kerby.kerberos.kerb.server.SimpleKdcServer;
import org.apache.kerby.util.NetworkUtil;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.File;
import java.net.HttpURLConnection;
import java.net.URL;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

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
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class KerberosAuthenticationIT extends BaseIT {
   // composition in favour of inheritance, due to KDC instance is used via TestExecutionListeners and Test both (shared)
   private static final String WORK_DIR = "target";
   private static final File KDC_WORK_DIR = new File(WORK_DIR);
   private static final File KEYTAB = new File(WORK_DIR + "/foo.keytab");
   private static final String CLIENT_PRINCIPAL = "client/localhost";
   private static final String TGT_PRINCIPAL = "HTTP/localhost";

   private static SimpleKdcServer simpleKdcServer;

   @Autowired
   private JobsRepository jobsRepository;

   @LocalServerPort
   int randomPort;

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

   private void createJob(String jobName, String teamName) throws Exception {
      String body = getDataJobRequestBody(jobName, teamName);

      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs", teamName))
                  .with(user("user"))
                  .content(body)
                  .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isCreated());
   }

   @Test
   public void testAuthenticatedCall() throws Exception {
      createJob("testjob", "testjob");

      SpnegoClient spnegoClient = SpnegoClient.loginWithKeyTab(CLIENT_PRINCIPAL, KEYTAB.getPath());
      URL url = new URL("http://127.0.0.1:" + randomPort + "/data-jobs/for-team/testjob/jobs/testjob");
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

   @AfterAll
   public void cleanup() throws KrbException {
      jobsRepository.deleteAll();
      KDC_WORK_DIR.deleteOnExit();
      simpleKdcServer.stop();
   }

   @BeforeEach
   @Override
   public void startMiniKdc() throws Exception {
      // Do nothing since we use apache kerby for this test.
   }

   @AfterEach
   @Override
   public void stopMiniKdc() {
      // Do nothing since we use apache kerby for this test.
   }

}
