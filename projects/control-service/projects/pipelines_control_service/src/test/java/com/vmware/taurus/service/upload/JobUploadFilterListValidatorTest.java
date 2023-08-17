/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import static org.mockito.Mockito.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.endsWith;
import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;


public class JobUploadFilterListValidatorTest {

  static Path getTestJob() throws IOException {
    return Paths.get(new ClassPathResource("detect-job").getURI());
  }

  private JobUploadFilterListValidator createTestValidator(String[] extensions, String[] types) {
    var validator = new JobUploadFilterListValidator(extensions, types);
    var spy = spy(validator);
    // We don't want to actually delete the files. Delete method is tested in a different test class.
    doNothing().when(spy).processMatchedFile(any(), any(), any());
    return spy;
  }

  @Test
  void test_ValidateExtensionType_emptyLists() throws IOException {
    var validator = createTestValidator(new String[]{}, new String[]{});

    validator.validateJob("foo", getTestJob());
    // empty lists, expect no filtered files
    verify(validator, times(0))
        .processMatchedFile(any(), any(), any());
  }

  @Test
  void test_ValidateExtension_expectDeletion() throws IOException {
    var validator = createTestValidator(new String[]{"py"}, new String[]{});

    validator.validateJob("foo", getTestJob());
    //check if all 3 files that end in py are deleted
    verify(validator, times(3))
        .processMatchedFile(any(), any(), endsWith("py"));
  }

  @Test
  void test_ValidateExtensionType_expectDeletion() throws IOException {
    var validator = createTestValidator(new String[]{"py"},
        new String[]{"application/octet-stream"});

    validator.validateJob("foo", getTestJob());
    // we have exactly 3 files that end in py
    verify(validator, times(4))
        .processMatchedFile(any(), any(), any());
    // check if the binary file was deleted.
    verify(validator, times(1))
        .processMatchedFile(any(), any(), eq("package/binary"));
  }

  @Test
  void test_ValidateType_expectDeletion() throws IOException {
    var validator = createTestValidator(new String[]{},
        new String[]{"application/octet-stream"});
    validator.validateJob("foo", getTestJob());
    verify(validator, times(1))
        .processMatchedFile(any(), any(), eq("package/binary"));
  }

  @Test
  void test_ValidateType_multipleFilterTypes_expectDeletion() throws IOException {
    var validator = createTestValidator(new String[]{},
        new String[]{"application/octet-stream", "application/x-executable"});
    validator.validateJob("foo", getTestJob());
    //verify the binary file was deleted
    verify(validator, times(1))
        .processMatchedFile(any(), any(), eq("package/binary"));
    //verify no other deletions performed
    verify(validator, times(1))
        .processMatchedFile(any(), any(), any());
  }

  @Test
  void test_ValidateExtensionType_multipleMatches_expectDeletion() throws IOException {
    var validator = createTestValidator(new String[]{"py", "ini"},
        new String[]{"application/octet-stream", "text/x-sql"});

    validator.validateJob("foo", getTestJob());
    // check all 6 files are deleted.
    verify(validator, times(6))
        .processMatchedFile(any(), any(), any());
  }
}
