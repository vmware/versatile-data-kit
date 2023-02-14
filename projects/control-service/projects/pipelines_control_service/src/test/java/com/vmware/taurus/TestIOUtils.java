/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import lombok.SneakyThrows;
import org.junit.jupiter.api.Assertions;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public final class TestIOUtils {

  public static void compareDirectories(File expectedDirectory, File actualDirectory)
      throws IOException {
    Files.walk(expectedDirectory.toPath())
        .forEach(
            expected -> {
              // System.out.println(expected);
              Path actual =
                  new File(
                          actualDirectory,
                          expectedDirectory.toPath().relativize(expected).toString())
                      .toPath();
              if (expected.toFile().isDirectory()) {
                Assertions.assertTrue(
                    actual.toFile().isDirectory(), "Expected directory: " + actual);
              } else {
                Assertions.assertTrue(actual.toFile().isFile(), "Expected file: " + actual);
                Assertions.assertEquals(fileToString(expected), fileToString(actual));
              }
            });
    Files.walk(actualDirectory.toPath())
        .forEach(
            actual -> {
              Path expected =
                  new File(
                          expectedDirectory, actualDirectory.toPath().relativize(actual).toString())
                      .toPath();
              if (!expected.toFile().exists()) {
                Assertions.fail("Did not expect this file or directory: " + actual);
              }
            });
  }

  @SneakyThrows
  private static String fileToString(Path filePath) {
    return Files.readString(filePath);
  }
}
