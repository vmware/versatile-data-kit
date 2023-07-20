/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.junit.jupiter.api.Test;

import static com.vmware.taurus.service.deploy.DockerImageName.getImagePath;
import static com.vmware.taurus.service.deploy.DockerImageName.updateImageWithTag;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class DockerImageNameTest {

  @Test
  void testGetTag() {
    assertEquals("tag", DockerImageName.getTag("domain:5000/name:tag"));
    assertEquals("v1.0.1", DockerImageName.getTag("name:v1.0.1"));
    assertEquals("v1.0.2", DockerImageName.getTag("foo.bar/name:v1.0.2"));
    assertEquals("latest", DockerImageName.getTag("foo.bar/name"));
    assertEquals("latest", DockerImageName.getTag("domain:5000/name"));
  }

  @Test
  void testUpdateImageWithTag() {
    assertEquals("domain:5000/name:tag2", updateImageWithTag("domain:5000/name:tag", "tag2"));
    assertEquals("name:v5", updateImageWithTag("name:v1.0.1", "v5"));
    assertEquals("foo.bar/name:v6", updateImageWithTag("foo.bar/name:v1.0.2", "v6"));

    assertEquals("name:tag", updateImageWithTag("name", "tag"));
    assertEquals("domain:5000/name:tag", updateImageWithTag("domain:5000/name", "tag"));
  }

  @Test
  public void testGetImageName() {
    assertEquals("alpine", getImagePath("alpine:latest"));
    assertEquals("image", getImagePath("gcr.io/image:latest"));
    assertEquals("project/another-image", getImagePath("gcr.io/project/another-image:1.0.0"));
    assertEquals(
        "namespace/subnamespace/image",
        getImagePath("registry.com/namespace/subnamespace/image:tag"));
  }

  @Test
  public void testGetImageNameWithNoTag() {
    assertEquals("project/yet-another-image", getImagePath("docker.io/project/yet-another-image"));
  }

  @Test
  public void testGetImageNameWithPortInURL() {
    assertEquals(
        "my-namespace/my-image", getImagePath("localhost:5000/my-namespace/my-image:latest"));
  }
}
