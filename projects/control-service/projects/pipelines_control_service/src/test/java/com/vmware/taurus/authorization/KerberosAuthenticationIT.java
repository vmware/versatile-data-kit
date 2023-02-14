/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.authorization;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.KerberosUtil;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import org.apache.kerby.kerberos.kerb.KrbException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * This test is in the unit tests directory, because: A) it's fast (it takes a few seconds) B) It
 * mocks and manages all its dependencies and does not create side effects . C) It does not work
 * well with MiniKDC e.g Our integration tests use the MiniKdc server provided by spring which as of
 * today hasn't received any updates in a long time and is problematic. However, minikdc leaves some
 * files and configurations that interfere with apache kerby and both tests cannot run on the same
 * runner (even after invoking the provided cleanup mehtods by the libraries). We should look into
 * migrating to apache kerby for our integration tests too.
 */
@TestPropertySource(
    properties = {
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
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@ExtendWith(SpringExtension.class)
public class KerberosAuthenticationIT extends TestKerberosServerHelper {

  @Autowired private JobsRepository jobsRepository;

  private DataJob dataJob;

  @LocalServerPort int randomPort;

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
    URL requestUrl =
        new URL("http://127.0.0.1:" + randomPort + "/data-jobs/for-team/test-team/jobs/test-name");
    var krb5 = getSimpleKdcServer().getKrbClient().getKrbConfig();
    URL authUrl = new URL("http://" + krb5.getKdcHost() + "/" + krb5.getKdcPort());
    var res =
        KerberosUtil.requestWithKerberosAuth(
            requestUrl, authUrl, getCLIENT_PRINCIPAL(), getKEYTAB().getPath());
    Assertions.assertEquals(200, res.getResponseCode());
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
  public static void cleanup() throws KrbException, IOException {
    shutdownServer();
  }
}
