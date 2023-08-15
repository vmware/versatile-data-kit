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

@Slf4j
public abstract class AbstractJobFileValidator {

  /**
   * Returns a list of file types against which the validation logic will perform operations for the
   * currently validated user file.
   *
   * @return
   */
  abstract String[] getValidationTypes();

  /**
   * Performs an operation on user uploaded files which returns a formatted string used to check if
   * any match against the validation types. E.g. returns the apache tika file type, or file ending
   * etc.
   *
   * @param filePath
   * @return
   * @throws IOException
   */
  abstract String detectFileType(Path filePath) throws IOException;

  /**
   * Checks if the detected file type matches against one of the strings present in validation types
   * according to a condition which should be defined in the overriding class.
   *
   * @param detectedType
   * @return
   */
  abstract boolean matchTypes(String detectedType);

  /**
   * Performs operations on already matched files, such as throwing exception, logging or deleting.
   *
   * @param filePath
   * @param jobName
   * @param pathInsideJob
   * @throws IOException
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
   * @throws InvalidJobUpload
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

  void validateAllowedFiles(String jobName, Path jobDirectory) throws IOException {
    if (getValidationTypes().length == 0) {
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
      log.debug("Job {}'s file {} is of type {}", jobName, filePath, pathInsideJob);
      if (matchTypes(fileType)) {
        processMatchedFile(filePath, jobName, pathInsideJob.toString());
      }
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format("Unable to open and process file %s", pathInsideJob),
          e);
    }
  }
}
