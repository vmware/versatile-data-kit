/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import java.nio.file.Path;
import java.util.Arrays;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * This class filters out the job directory from forbidden files so that it can be uploaded without
 * them. Forbidden files are specified in a comma separated list in apache tika format, or file
 * extensions. Full list of supported files can be found - https://tika.apache.org ; This operation
 * is intended to allow the upload of a data job by deleting any files specified in the:
 * upload.validation.fileTypes.filterlist property.
 */
@Service
@Slf4j
public class JobUploadFilterListValidator extends AbstractJobFileValidator {

  private final String[] filterListExtensions;
  private final String[] filterListTypes;
  private final FileFormatDetector formatDetector;

  public JobUploadFilterListValidator(
      @Value("${upload.validation.fileExtensions.filterlist:}") String[] filterListExtensions,
      @Value("${upload.validation.fileTypes.filterlist:}") String[] filterListTypes) {
    this.filterListExtensions = filterListExtensions;
    this.filterListTypes = filterListTypes;
    this.formatDetector = new FileFormatDetector();
  }

  @Override
  String[] getValidationTypes() {
    return this.filterListTypes;
  }

  @Override
  String[] getValidationExtensions() {
    return this.filterListExtensions;
  }

  @Override
  boolean matchTypes(String detectedType, String detectedExtension) {
    return Arrays.stream(getValidationExtensions()).anyMatch(detectedExtension::endsWith)
        || Arrays.stream(getValidationTypes())
            .anyMatch(validationType -> formatDetector.matchTypes(detectedType, validationType));
  }

  @Override
  void processMatchedFile(Path filePath, String jobName, String pathInsideJob) {
    log.debug(
        "Deleting file: {}, from job: {}, before uploading to version control.",
        pathInsideJob,
        jobName);

    if (!filePath.toFile().delete()) {
      throw new InvalidJobUpload(
          jobName,
          String.format(
              "File: %s was scheduled for deletion before uploading"
                  + " job code to version control but the operation was unsuccessful.",
              pathInsideJob),
          "Remove the file locally from your data job and deploy it again. "
              + "List of file types that will be scheduled for deletion "
              + Arrays.toString(getValidationTypes())
              + " List of file extensions that will be scheduled for deletion "
              + Arrays.toString(getValidationExtensions()));
    }
  }
}
