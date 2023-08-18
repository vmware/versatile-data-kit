/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.exception.ExternalSystemError;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FilenameUtils;

@Slf4j
public abstract class AbstractJobFileValidator {

  private final FileFormatDetector formatDetector = new FileFormatDetector();

  /** Returns a list of file types against which the validation logic should perform operations. */
  abstract String[] getValidationTypes();

  /**
   * Returns a list of file extensions against which the validation logic should perform operations.
   */
  abstract String[] getValidationExtensions();

  /**
   * Checks if the detected file type matches against one of the strings present in validation types
   * according to a condition which should be defined in the overriding class.
   */
  abstract boolean matchTypes(String detectedType, String detectedExtension);

  /**
   * Performs operations on already matched files, such as throwing exception, logging or deleting.
   */
  abstract void processMatchedFile(Path filePath, String jobName, String pathInsideJob)
      throws IOException;

  /**
   * Validate all files of a data job to be upto standard and do not contain anything forbidden. The
   * validation done is by detecting the file type and checking if that file type is allowed against
   * pre-configured list specified in the extending class. If the allowList is empty then all files
   * are allowed and no further processing is performed.
   *
   * @param jobName the name of the data job whose files are validated
   * @param jobDirectory path to the data job directory where unarchived content of the data job
   *     being uploaded can be seen.
   */
  public void validateJob(String jobName, Path jobDirectory) {
    try {
      validateAllowedFiles(jobName, jobDirectory);
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format("Unable to open and process job %s directory.", jobName),
          e);
    }
  }

  private void validateAllowedFiles(String jobName, Path jobDirectory) throws IOException {
    if (getValidationTypes().length == 0 && getValidationExtensions().length == 0) {
      log.debug(
          "List of validation files is empty. That means all files are allowed. No checks are"
              + " done.");
      return;
    }
    Files.walk(jobDirectory)
        .filter(p -> p.toFile().isFile())
        .forEach(filePath -> validateFile(jobName, filePath, jobDirectory.relativize(filePath)));
  }

  private void validateFile(String jobName, Path filePath, Path pathInsideJob)
      throws InvalidJobUpload {
    if (filePath.toFile().isDirectory()) {
      return;
    }
    try {
      var fileType = detectFileType(filePath);
      var fileExtension = detectFileExtension(filePath);
      log.debug("Job {}'s file {} is of type {}", jobName, filePath, pathInsideJob);
      if (matchTypes(fileType, fileExtension)) {
        processMatchedFile(filePath, jobName, pathInsideJob.toString());
      }
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format("Unable to open and process file %s", pathInsideJob),
          e);
    }
  }

  String detectFileType(Path filePath) throws IOException {
    return this.formatDetector.detectFileType(filePath);
  }

  String detectFileExtension(Path filePath) {
    return FilenameUtils.getExtension(filePath.getFileName().toString());
  }
}
