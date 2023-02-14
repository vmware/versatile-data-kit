/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;

class FileFormatDetectorTest {

  @Test
  void test_matchTypes_true() {
    Assertions.assertTrue(new FileFormatDetector().matchTypes("foo/bar", "foo/bar"));
    Assertions.assertTrue(new FileFormatDetector().matchTypes("text / plain", "text/plain"));
    Assertions.assertTrue(new FileFormatDetector().matchTypes("text / PLAIN", "text/plain"));
    Assertions.assertTrue(new FileFormatDetector().matchTypes("text/plain", "text"));
  }

  @Test
  void test_matchTypes_false() {
    Assertions.assertFalse(new FileFormatDetector().matchTypes("text/plain", "application"));
    Assertions.assertFalse(new FileFormatDetector().matchTypes("text/plain", "text/sql"));
  }

  @Test
  void test_matchTypes_errors() {
    Assertions.assertThrows(
        IllegalArgumentException.class, () -> new FileFormatDetector().matchTypes("", ""));
    Assertions.assertThrows(
        IllegalArgumentException.class, () -> new FileFormatDetector().matchTypes("type", "type"));
    Assertions.assertThrows(
        IllegalArgumentException.class,
        () -> new FileFormatDetector().matchTypes("type", "type/subtype"));
  }

  @Test
  void test_DetectType() throws IOException {
    var detector = new FileFormatDetector();
    Assertions.assertEquals(
        "application/json", detector.detectFileType(getResource("detect.json")));
    Assertions.assertEquals("image/jpeg", detector.detectFileType(getResource("detect.jpeg")));
    Assertions.assertEquals("text/x-sql", detector.detectFileType(getResource("detect.sql")));
  }

  @NotNull
  private Path getResource(String resource) throws IOException {
    return Paths.get(new ClassPathResource(resource).getURI());
  }
}
