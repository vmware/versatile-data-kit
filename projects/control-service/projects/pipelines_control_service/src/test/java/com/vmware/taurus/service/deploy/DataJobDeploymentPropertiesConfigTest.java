/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.ReadFrom;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.WriteTo;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ServiceApp.class)
public class DataJobDeploymentPropertiesConfigTest {

  @Autowired
  private DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  @Test
  public void testWriteToK8SProperty() {
    // testing default behaviour.
    Assertions.assertTrue(dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.K8S));
  }

  @Test
  public void testWriteToDBProperty() {
    // testing default behaviour.
    Assertions.assertTrue(dataJobDeploymentPropertiesConfig.getWriteTos().contains(WriteTo.DB));
  }

  @Test
  public void testReadFromProperty() {
    // testing default behaviour.
    Assertions.assertEquals(
        dataJobDeploymentPropertiesConfig.getReadDataSource(), ReadFrom.K8S);
  }

  @Test
  public void testReadSupportedValues() {
    Assertions.assertEquals(ReadFrom.valueOf("K8S"), ReadFrom.K8S);
    Assertions.assertEquals(ReadFrom.valueOf("DB"), ReadFrom.DB);
  }

  @Test
  public void testWriteToSupportedValues() {
    Assertions.assertEquals(WriteTo.valueOf("K8S"), WriteTo.K8S);
    Assertions.assertEquals(WriteTo.valueOf("DB"), WriteTo.DB);
  }
}
