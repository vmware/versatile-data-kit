/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
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
public class JobUploadFileFilter {

  private final String[] filterList;
  private FileFormatDetector formatDetector;

  public JobUploadFileFilter(
      @Value("${upload.validation.fileTypes.filterlist:}") String[] filterList) {
    this.filterList = filterList;
    this.formatDetector = new FileFormatDetector();
  }

  /**
   * Data job directory to be filtered from files present in the
   * upload.validation.fileTypes.filterlist variable. All matching files are deleted from the
   * directory and sub-directories before being uploaded to git version control.
   *
   * @param jobFolder
   * @param jobName
   */
  public void filterDirectory(File jobFolder, String jobName) {

    if (this.filterList.length == 0) {
      return;
    }

    try (Stream<Path> stream = Files.walk(Paths.get(jobFolder.getPath()))) {
      stream
          .filter(Files::isRegularFile)
          .forEach(
              file -> {
                validateFile(file.toAbsolutePath(), jobName);
              });
    } catch (IOException e) {
      log.error("Exception while processing filter list: {}", e);
      throw new InvalidJobUpload(
          jobName,
          "The control-service was unable to process the filter list of files.",
          "Please check for any corrupted files and try again or contact support.");
    }
  }

  private void validateFile(Path filePath, String jobName) {
    if (filePath.toFile().isDirectory()) {
      return;
    }
    try {
      String fileType = this.formatDetector.detectFileType(filePath);
      if (Arrays.stream(filterList)
          .anyMatch(allowed -> formatDetector.matchTypes(fileType, allowed))) {
        filePath.toFile().delete();
      }
    } catch (IOException e) {
      throw new InvalidJobUpload(
          jobName,
          "The control-service was unable to process the file: " + filePath.getFileName(),
          "Please check the file and fix any issues/try again or contact support.");
    }
  }
}
