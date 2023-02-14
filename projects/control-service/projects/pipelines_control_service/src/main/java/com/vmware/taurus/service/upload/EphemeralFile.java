/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.exception.ErrorMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * Responsible for abstracting a file into an AutoClosable file. If one of these are created at the
 * start of a try with resources block then the file will be deleted at the end of the try block.
 */
public class EphemeralFile implements AutoCloseable {
  private static final Logger log = LoggerFactory.getLogger(EphemeralFile.class);

  private static final String TEMPORARY_DIRECTORY_PREFIX = "job_";
  private final Path file;
  private final String jobName;
  private final String action;

  public EphemeralFile(String datajobsTempStorageFolder, String jobName, String action)
      throws IOException {
    if (StringUtils.hasLength(datajobsTempStorageFolder)) {
      this.file =
          Paths.get(datajobsTempStorageFolder)
              .resolve(TEMPORARY_DIRECTORY_PREFIX + UUID.randomUUID());
    } else {
      this.file = FileUtils.createTempDir(TEMPORARY_DIRECTORY_PREFIX);
    }
    this.jobName = jobName;
    this.action = action;
  }

  public File toFile() {
    return file.toFile();
  }

  @Override
  public void close() {
    try {
      FileUtils.removeDir(file);
    } catch (IOException e) {
      log.warn(
          new ErrorMessage(
                  String.format(
                      "Unable to clean up temporary files while trying to %s: %s", action, jobName),
                  String.format("Error: %s", e.getMessage()),
                  "Operation may be successful, but temporary files are left on the file"
                      + " system.",
                  "Contact the provider to resolve the issue or clean up the temporary files"
                      + " manually.")
              .toString(),
          e);
    }
  }
}
