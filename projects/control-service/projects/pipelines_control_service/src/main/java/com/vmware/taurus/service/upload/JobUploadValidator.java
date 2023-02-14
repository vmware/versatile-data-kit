/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.exception.ExternalSystemError;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

@Service
class JobUploadValidator {
  private final Logger log = LoggerFactory.getLogger(this.getClass());

  /**
   * List of files that are allowed to be uploaded. Full list of file types are documented in
   * https://tika.apache.org/2.5.0/formats.html#Full_list_of_Supported_Formats_in_standard_artifacts
   * If set to empty, then all files are allowed using the allowlist.
   */
  private final String[] allowlist;

  private final FileFormatDetector formatDetector;

  public JobUploadValidator(
      @Value("${upload.validation.fileTypes.allowlist:}") String[] allowList) {
    this.allowlist = allowList;
    this.formatDetector = new FileFormatDetector();
    log.debug("Job sources upload validator allowlist: {}", Arrays.toString(allowList));
  }

  /**
   * Validate all files of a data job that are being upto standard and are not containing anything
   * forbidden. The validation done is by detecting the file type and checking if that file type is
   * allowed against preconfigurd list controlled by "upload.validation.fileTypes.allowlist". If the
   * allowList is empty then all files are allowed.
   *
   * @param jobName the name of the data job whose files are validated
   * @param jobDirectory path to the data job directory where unarchived content of the data job
   *     being uploaded can be seen.
   * @throws InvalidJobUpload
   */
  public void validateJob(String jobName, Path jobDirectory) throws InvalidJobUpload {
    validateAllowedFiles(jobName, jobDirectory);
  }

  private void validateAllowedFiles(String jobName, Path jobDirectory) {
    if (this.allowlist.length == 0) {
      log.debug(
          "List of allowed files is empty. That means all files are allowed. No checks are done.");
      return;
    }
    try {
      Files.walk(jobDirectory)
          .filter(p -> p.toFile().isFile())
          .forEach(filePath -> validateFile(jobName, filePath, jobDirectory.relativize(filePath)));
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format("Unable to open and process job %s directory.", jobName),
          e);
    }
  }

  /**
   * Validate the file in a data job based on its file type : If allowed list is NOT empty and it's
   * NOT in allowed list, InvalidJobUpload is raised otherwise the file is allowed
   */
  private void validateFile(String jobName, Path filePath, Path pathInsideJob)
      throws InvalidJobUpload {
    if (filePath.toFile().isDirectory()) {
      return;
    }
    try {
      var fileType = this.formatDetector.detectFileType(filePath);
      log.debug("Job {}'s file {} is of type {}", jobName, filePath, pathInsideJob);
      if (Arrays.stream(allowlist)
          .noneMatch(allowed -> formatDetector.matchTypes(fileType, allowed))) {
        throw new InvalidJobUpload(
            jobName,
            String.format(
                "file '%s' was detected to be of type '%s' "
                    + "and it is not in the allowed list of file types.",
                pathInsideJob, fileType),
            "Make sure to remove the forbidden file. "
                + "Current list of allowed file types is "
                + Arrays.toString(allowlist));
      }
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format("Unable to open and process file %s", pathInsideJob),
          e);
    }
  }
}
