/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.kerb4j.client.SpnegoClient;
import com.kerb4j.client.SpnegoContext;
import org.ietf.jgss.GSSException;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.PrivilegedActionException;

public class KerberosUtil {
   public static HttpURLConnection requestWithKerberosAuth(URL requestURL, URL kdcAuthURL,
                                                           String clientPrincipal, String keytabLocation)
         throws IOException, PrivilegedActionException, GSSException {

      SpnegoClient spnegoClient = SpnegoClient.loginWithKeyTab(clientPrincipal, keytabLocation);
      SpnegoContext context = spnegoClient.createContext(kdcAuthURL);
      HttpURLConnection conn = (HttpURLConnection) requestURL.openConnection();
      conn.setRequestProperty("Authorization", context.createTokenAsAuthroizationHeader());
      return conn;

   }
}
