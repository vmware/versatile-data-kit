/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class DockerImageNameTest {

  @Test
  void testGetTag() {
    Assertions.assertEquals("tag", DockerImageName.getTag("domain:5000/name:tag"));
    Assertions.assertEquals("v1.0.1", DockerImageName.getTag("name:v1.0.1"));
    Assertions.assertEquals("v1.0.2", DockerImageName.getTag("foo.bar/name:v1.0.2"));
    Assertions.assertEquals("latest", DockerImageName.getTag("foo.bar/name"));
    Assertions.assertEquals("latest", DockerImageName.getTag("domain:5000/name"));
  }

  @Test
  void testUpdateImageWithTag() {
    Assertions.assertEquals(
        "domain:5000/name:tag2",
        DockerImageName.updateImageWithTag("domain:5000/name:tag", "tag2"));
    Assertions.assertEquals("name:v5", DockerImageName.updateImageWithTag("name:v1.0.1", "v5"));
    Assertions.assertEquals(
        "foo.bar/name:v6", DockerImageName.updateImageWithTag("foo.bar/name:v1.0.2", "v6"));

    Assertions.assertEquals("name:tag", DockerImageName.updateImageWithTag("name", "tag"));
    Assertions.assertEquals(
        "domain:5000/name:tag", DockerImageName.updateImageWithTag("domain:5000/name", "tag"));
  }
}
