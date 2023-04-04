/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobApiInfo;
import com.vmware.taurus.service.UserAgentService;
import com.vmware.taurus.service.deploy.SupportedPythonVersions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

public class DataJobsServiceControllerTest {

  @Test
  public void testInfo() {
    // Mock dependencies
    UserAgentService userAgentService = Mockito.mock(UserAgentService.class);
    SupportedPythonVersions supportedPythonVersions = Mockito.mock(SupportedPythonVersions.class);

    // Create instance of DataJobsServiceController
    DataJobsServiceController controller =
        new DataJobsServiceController(userAgentService, supportedPythonVersions);

    // Prepare test data
    Set<String> supportedVersions = new HashSet<>();
    supportedVersions.add("python3.6");
    supportedVersions.add("python3.7");
    supportedVersions.add("python3.8");
    supportedVersions.add("python3.9");
    when(supportedPythonVersions.getSupportedPythonVersions()).thenReturn(supportedVersions);
    when(userAgentService.getUserAgentDetails()).thenReturn("1.0.0");

    // Call the API method
    ResponseEntity<DataJobApiInfo> responseEntity = controller.info("myteam");

    // Verify the response status code
    assertEquals(HttpStatus.OK, responseEntity.getStatusCode());

    // Verify the response body
    DataJobApiInfo response = responseEntity.getBody();
    assertEquals("1.0.0", response.getApiVersion());
    assertEquals(new ArrayList<>(supportedVersions), response.getSupportedPythonVersions());
  }
}
