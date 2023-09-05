/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.deploy.DataJobDeploymentPropertiesConfig.PropertyPersistence;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentPropertiesConfigTest {

  @Autowired
  private DataJobDeploymentPropertiesConfig dataJobDeploymentPropertiesConfig;

  @Test
  public void testWriteToK8SProperty() {
    //testing default behaviour.
    Assertions.assertTrue(dataJobDeploymentPropertiesConfig.isWriteToK8S());
  }

  @Test
  public void testWriteToDBProperty() {
    //testing default behaviour.
    Assertions.assertTrue(dataJobDeploymentPropertiesConfig.isWriteToDB());
  }

  @Test
  public void testReadFromProperty() {
    //testing default behaviour.
    Assertions.assertEquals(dataJobDeploymentPropertiesConfig.getReadDataSource(),
        PropertyPersistence.K8S);
  }

  @Test
  public void testSupportedValues() {
    Assertions.assertEquals(PropertyPersistence.valueOf("K8S"), PropertyPersistence.K8S);
    Assertions.assertEquals(PropertyPersistence.valueOf("DB"), PropertyPersistence.DB);
  }
}
