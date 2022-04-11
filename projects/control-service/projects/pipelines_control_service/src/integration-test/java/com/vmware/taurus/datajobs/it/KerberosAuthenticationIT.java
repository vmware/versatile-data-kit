/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.google.common.io.Files;
import com.sun.security.auth.callback.TextCallbackHandler;
import com.vmware.taurus.ServiceApp;
import org.junit.Assert;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.security.kerberos.client.KerberosRestTemplate;
import org.springframework.security.kerberos.test.KerberosSecurityTestcase;
import org.springframework.security.kerberos.test.MiniKdc;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import javax.security.auth.Subject;
import javax.security.auth.kerberos.KerberosPrincipal;
import javax.security.auth.login.AppConfigurationEntry;
import javax.security.auth.login.Configuration;
import javax.security.auth.login.LoginContext;
import java.io.File;
import java.security.Principal;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Properties;
import java.util.Set;


@TestPropertySource(properties = {
      "datajobs.security.kerberos.enabled=true",
      "featureflag.security.enabled=true",
      "datajobs.security.kerberos.kerberosPrincipal=\"pa__view_foo\"",
      "datajobs.security.kerberos.keytabFileLocation=target/foo.keytab",
      "datajobs.security.kerberos.krb5ConfigLocation=target/krb5.conf"
})
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ServiceApp.class)
@ExtendWith(SpringExtension.class)
//@AutoConfigureMockMvc
public class KerberosAuthenticationIT {

   private static KerberosSecurityTestcase kerberosSecurityTestcase;
   private static Properties kdcConf;
   private static File krb5;
   private static Set<Principal> principals = new HashSet<Principal>();
   private static File keytab;
   private static MiniKdc kdc;
   private static String principal = "pa__view_foo";


//   @Autowired
//   protected MockMvc mockMvc;

   @LocalServerPort
   int randomPort;

   static {
      try {
         kerberosSecurityTestcase = new KerberosSecurityTestcase();
         kerberosSecurityTestcase.getConf();
         kerberosSecurityTestcase.startMiniKdc();
         kdc = kerberosSecurityTestcase.getKdc();
         kdcConf = kerberosSecurityTestcase.getConf();
         File workDir = kerberosSecurityTestcase.getWorkDir();
         krb5 = kdc.getKrb5conf();

         keytab = new File(workDir, "foo.keytab");
         File configurationKrb = new File(workDir, "krb5.conf");
         kdc.createPrincipal(keytab, principal);

         principals.add(new KerberosPrincipal(principal));
         Files.copy(krb5, configurationKrb);
         System.setProperty("java.security.krb5.conf", krb5.getAbsolutePath());
         System.setProperty("sun.security.krb5.debug", "true");
      } catch (Exception e) {
         throw new RuntimeException("Unable to start mini KDC service for Integration Test.", e);
      }
   }

   @BeforeEach
   public void setup() {

   }

   @Test
   public void test() throws Exception {

      Subject subject = new Subject(false, principals, new HashSet<Object>(), new HashSet<Object>());
      var loginContext = new LoginContext("", subject, new TextCallbackHandler(), KerberosConfiguration.createClientConfig(principal,
            keytab));
      loginContext.login();
      subject = loginContext.getSubject();
      Assert.assertEquals(1, subject.getPrincipals().size());
      Assert.assertEquals(KerberosPrincipal.class, subject.getPrincipals().iterator().next().getClass());
      Assert.assertEquals(principal + "@" + kdc.getRealm(), subject.getPrincipals().iterator().next().getName());

      // Get ticket from login context
//
//      KerberosTicket kerberosTicket = null;
//
//      for (var object : subject.getPrivateCredentials()) {
//         if (object instanceof KerberosTicket) {
//            kerberosTicket = (KerberosTicket) object;
//         }
//      }

      KerberosRestTemplate kerberosRestTemplate = new KerberosRestTemplate(keytab.getPath(), principal);
      var response = kerberosRestTemplate.getForObject("http://localhost:" + randomPort + "/data-jobs/for-team/supercollider/jobs", String.class);

   }

   @AfterAll
   public static void cleanup() {
      kerberosSecurityTestcase.stopMiniKdc();
   }

   private static class KerberosConfiguration extends Configuration {
      private String principal;
      private String keytab;
      private boolean isInitiator;

      private KerberosConfiguration(String principal, File keytab, boolean client) {
         this.principal = principal;
         this.keytab = keytab.getAbsolutePath();
         this.isInitiator = client;
      }

      public static Configuration createClientConfig(String principal, File keytab) {
         return new KerberosConfiguration(principal, keytab, true);
      }

      public static Configuration createServerConfig(String principal, File keytab) {
         return new KerberosConfiguration(principal, keytab, false);
      }

      private static String getKrb5LoginModuleName() {
         return System.getProperty("java.vendor").contains("IBM") ? "com.ibm.security.auth.module.Krb5LoginModule"
               : "com.sun.security.auth.module.Krb5LoginModule";
      }

      @Override
      public AppConfigurationEntry[] getAppConfigurationEntry(String name) {
         Map<String, String> options = new HashMap<String, String>();
         options.put("keyTab", keytab);
         options.put("principal", principal);
         options.put("useKeyTab", "true");
         options.put("storeKey", "true");
         options.put("doNotPrompt", "true");
         options.put("useTicketCache", "true");
         options.put("renewTGT", "true");
         options.put("refreshKrb5Config", "true");
         options.put("isInitiator", Boolean.toString(isInitiator));
         String ticketCache = System.getenv("KRB5CCNAME");
         if (ticketCache != null) {
            options.put("ticketCache", ticketCache);
         }
         options.put("debug", "true");

         return new AppConfigurationEntry[]{new AppConfigurationEntry(getKrb5LoginModuleName(),
               AppConfigurationEntry.LoginModuleControlFlag.REQUIRED, options)};
      }
   }

}
