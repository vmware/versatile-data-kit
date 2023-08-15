/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;

class JobUploadAllowListValidatorTest {

  /**
   * The testing job has the following structure: ├── config.ini ├── package │ ├── binary │ ├──
   * lib.py │ └── subpackage │ └── other.py ├── step.py └── step.sql
   */
  static Path getTestJob() throws IOException {
    return Paths.get(new ClassPathResource("detect-job").getURI());
  }

  @Test
  void test_validateJobAllowedWhenAllowListIsEmpty() throws IOException {
    JobUploadAllowListValidator validator = new JobUploadAllowListValidator(new String[] {});
    validator.validateJob("foo", getTestJob());
  }

  @Test
  void test_validateJobAllowed_base_types() throws IOException {
    JobUploadAllowListValidator validator =
        new JobUploadAllowListValidator(new String[] {"text", "application/octet-stream"});
    validator.validateJob("foo", getTestJob());
  }

  @Test
  void test_validateJobAllowed_full_types() throws IOException {
    JobUploadAllowListValidator validator =
        new JobUploadAllowListValidator(
            new String[] {"application/octet-stream", "text/x-ini", "text/x-sql", "text/x-python"});
    validator.validateJob("foo", getTestJob());
  }

  @Test
  void test_validateJobAllowed_not_allowed_sql_extension() {
    JobUploadAllowListValidator validator =
        new JobUploadAllowListValidator(
            new String[] {"application/octet-stream", "text/x-ini", "text/x-python"});
    Assertions.assertThrows(
        InvalidJobUpload.class, () -> validator.validateJob("foo", getTestJob()));
  }

  @Test
  void test_validateFileNotAllowed_binary() {
    JobUploadAllowListValidator validator = new JobUploadAllowListValidator(new String[] {"text"});
    Assertions.assertThrows(
        InvalidJobUpload.class, () -> validator.validateJob("foo", getTestJob()));
  }
}
