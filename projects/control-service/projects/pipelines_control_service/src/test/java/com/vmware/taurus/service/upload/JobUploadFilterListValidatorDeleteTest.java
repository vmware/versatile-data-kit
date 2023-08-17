/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.ControlplaneApplication;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.TrueFileFilter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(properties = {"upload.validation.fileExtensions.filterlist=pyc"})
public class JobUploadFilterListValidatorDeleteTest {

  @Autowired private JobUploadFilterListValidator jobUploadFilterListValidator;

  static Path getTestJob() throws IOException {
    return Paths.get(new ClassPathResource("filter-job").getURI());
  }

  @Test
  void testDeletePycFileBeforeUpload() throws IOException {
    var jobDirectoryFiles =
        FileUtils.listFiles(
            getTestJob().toFile(), TrueFileFilter.INSTANCE, TrueFileFilter.INSTANCE);

    boolean pycFileExists =
        jobDirectoryFiles.stream()
            .anyMatch(file -> file.toString().endsWith("10_python_step.cpython-39.pyc"));
    Assertions.assertTrue(pycFileExists);
    Assertions.assertEquals(jobDirectoryFiles.stream().count(), 6);

    jobUploadFilterListValidator.validateJob("test-job", getTestJob());

    jobDirectoryFiles =
        FileUtils.listFiles(
            getTestJob().toFile(), TrueFileFilter.INSTANCE, TrueFileFilter.INSTANCE);
    pycFileExists =
        jobDirectoryFiles.stream()
            .anyMatch(file -> file.toString().endsWith("10_python_step.cpython-39.pyc"));
    Assertions.assertFalse(pycFileExists);
    Assertions.assertEquals(jobDirectoryFiles.stream().count(), 5);
  }
}
