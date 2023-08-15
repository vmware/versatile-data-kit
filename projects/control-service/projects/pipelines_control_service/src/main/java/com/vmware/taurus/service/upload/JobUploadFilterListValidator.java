/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import java.nio.file.Path;
import java.util.Arrays;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FilenameUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * This class filters out the job directory from forbidden files so that it can be uploaded without
 * them. Forbidden files are specified in a comma separated list in apache tika format. Full list of
 * supported files can be found - https://tika.apache.org ; This operation is intended to allow the
 * upload of a data job by deleting any files specified in the:
 * upload.validation.fileTypes.filterlist property.
 */
@Service
@Slf4j
public class JobUploadFilterListValidator extends AbstractJobFileValidator {

  private final String[] filterList;

  public JobUploadFilterListValidator(
      @Value("${upload.validation.fileTypes.filterlist:}") String[] filterList) {
    this.filterList = filterList;
  }

  @Override
  String[] getValidationTypes() {
    return this.filterList;
  }

  @Override
  String detectFileType(Path filePath) {
    return FilenameUtils.getExtension(filePath.getFileName().toString());
  }

  @Override
  boolean matchTypes(String detectedType) {
    return Arrays.stream(getValidationTypes())
        .anyMatch(validationType -> detectedType.endsWith(validationType));
  }

  @Override
  void processMatchedFile(Path filePath, String jobName, String pathInsideJob) {
    log.debug(
        "Deleting file: {}, from job: {}, before uploading to version control.",
        pathInsideJob,
        jobName);
    filePath.toFile().delete();
  }
}
