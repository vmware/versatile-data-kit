/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
class JobUploadAllowListValidator extends AbstractJobFileValidator {

  private final Logger log = LoggerFactory.getLogger(this.getClass());

  /**
   * List of files that are allowed to be uploaded. Full list of file types are documented in
   * https://tika.apache.org/2.5.0/formats.html#Full_list_of_Supported_Formats_in_standard_artifacts
   * If set to empty, then all files are allowed using the allowlist.
   */
  private final String[] allowlist;

  private final FileFormatDetector formatDetector;

  public JobUploadAllowListValidator(
      @Value("${upload.validation.fileTypes.allowlist:}") String[] allowList) {
    this.allowlist = allowList;
    this.formatDetector = new FileFormatDetector();
    log.debug("Job sources upload validator allowlist: {}", Arrays.toString(allowList));
  }

  @Override
  String[] getValidationTypes() {
    return this.allowlist;
  }

  @Override
  String detectFileType(Path filePath) throws IOException {
    return this.formatDetector.detectFileType(filePath);
  }

  /**
   * Validate the file in a data job based on its file type : Checking if it's NOT in allowed list,
   * the processMatchedFile method is called otherwise the file is allowed and no processing is
   * performed.
   */
  @Override
  boolean matchTypes(String detectedType) {
    return Arrays.stream(getValidationTypes())
        .noneMatch(validationType -> formatDetector.matchTypes(detectedType, validationType));
  }

  @Override
  void processMatchedFile(Path filePath, String jobName, String pathInsideJob) throws IOException {
    throw new InvalidJobUpload(
        jobName,
        String.format(
            "file '%s' was detected to be of type '%s' "
                + "and it is not in the allowed list of file types.",
            pathInsideJob, detectFileType(filePath)),
        "Make sure to remove the forbidden file. "
            + "Current list of allowed file types is "
            + Arrays.toString(getValidationTypes()));
  }
}
