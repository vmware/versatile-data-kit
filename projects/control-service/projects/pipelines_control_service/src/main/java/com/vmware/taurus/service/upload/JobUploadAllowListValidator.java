/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@Slf4j
class JobUploadAllowListValidator extends AbstractJobFileValidator {

  /**
   * List of files that are allowed to be uploaded. Full list of file types are documented in
   * https://tika.apache.org/2.5.0/formats.html#Full_list_of_Supported_Formats_in_standard_artifacts
   * If set to empty, then all files are allowed using the allowlist.
   */
  private final String[] allowListTypes;

  private final String[] allowListExtensions;

  private final FileFormatDetector formatDetector;

  public JobUploadAllowListValidator(
      @Value("${upload.validation.fileTypes.allowlist:}") String[] allowListTypes,
      @Value("${upload.validation.fileExtensions.allowlist:}") String[] allowListExtensions) {
    this.allowListTypes = allowListTypes;
    this.allowListExtensions = allowListExtensions;
    this.formatDetector = new FileFormatDetector();
    log.debug(
        "Job sources upload validator allowlistTypes: {} allowListExtensions: {}",
        Arrays.toString(allowListTypes),
        Arrays.toString(allowListExtensions));
  }

  @Override
  String[] getValidationTypes() {
    return this.allowListTypes;
  }

  @Override
  String[] getValidationExtensions() {
    return this.allowListExtensions;
  }

  /**
   * Validate the file in a data job based on its file type : Checking if it's NOT in allowed list,
   * the processMatchedFile method is called otherwise the file is allowed and no processing is
   * performed.
   */
  @Override
  boolean matchTypes(String detectedType, String detectedExtension) {
    return matchTypes(detectedType) || matchExtensions(detectedExtension);
  }

  /** If the list of validationTypes is empty, all types are allowed. */
  private boolean matchTypes(String detectedType) {
    if (getValidationTypes().length == 0) {
      return false;
    }
    return Arrays.stream(getValidationTypes())
        .noneMatch(validationType -> formatDetector.matchTypes(detectedType, validationType));
  }

  /** If the list of validationExtensions is empty, all extensions are allowed. */
  private boolean matchExtensions(String detectedExtension) {
    if (getValidationExtensions().length == 0) {
      return false;
    }
    return Arrays.stream(getValidationExtensions()).noneMatch(detectedExtension::endsWith);
  }

  @Override
  void processMatchedFile(Path filePath, String jobName, String pathInsideJob) throws IOException {
    throw new InvalidJobUpload(
        jobName,
        String.format(
            "file '%s' was detected to be of type '%s' and extension '%s' "
                + "and it is not in the allowed list of file types or allowed extensions.",
            pathInsideJob, detectFileType(filePath), detectFileExtension(filePath)),
        "Make sure to remove the forbidden file. "
            + "Current list of allowed file types is "
            + Arrays.toString(getValidationTypes())
            + "Current list of allowed file extensions is "
            + Arrays.toString(getValidationExtensions()));
  }
}
