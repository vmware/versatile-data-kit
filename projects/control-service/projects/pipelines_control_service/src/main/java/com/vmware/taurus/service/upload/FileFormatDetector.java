/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import org.apache.tika.config.TikaConfig;
import org.apache.tika.detect.Detector;
import org.apache.tika.io.TikaInputStream;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.metadata.TikaCoreProperties;
import org.apache.tika.mime.MediaType;

import java.io.IOException;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

class FileFormatDetector {

  private final Map<String, MediaType> cachedMediaTypes = new HashMap<>();
  private final Detector detector;

  public FileFormatDetector() {
    // https://tika.apache.org/2.5.0/detection.html
    TikaConfig config = TikaConfig.getDefaultConfig();
    this.detector = config.getDetector();
  }

  /**
   * Match detectedType with target type: If targetType is base type (e.g text and not text/plain).
   * It will match with base type of the detected type. If targetType is full type and subtype
   * (text/plain) , it will match exactly.
   *
   * <p>Examples match("text/binary", "text/binary") returns True match("text/plain", "text")
   * returns True match("text/sql", "text/plain") returns False match("text/plain", "application")
   * returns False
   *
   * @param detectedType the type that was detected and need to be verified (must in format
   *     "type/subtype")
   * @param targetType the target type against which it is checked (can be either "type" or
   *     "type/subtype")
   * @return true or false
   */
  public boolean matchTypes(String detectedType, String targetType) {
    var detectedMediaType = cachedMediaTypes.computeIfAbsent(detectedType, MediaType::parse);
    if (detectedMediaType == null) {
      throw new IllegalArgumentException(
          "detectedType must in format 'type/subtype' but it was: " + detectedType);
    }
    if (targetType.contains("/")) { // compare by both type and subtype (text/plain)
      var targetMediaType = cachedMediaTypes.computeIfAbsent(targetType, MediaType::parse);
      return detectedMediaType.equals(targetMediaType);
    } else { // we compare only by type (text)
      return detectedMediaType.getType().equals(targetType);
    }
  }

  /**
   * Return the detected file type Full list of file types are documented in
   * https://tika.apache.org/2.5.0/formats.html#Full_list_of_Supported_Formats
   */
  public String detectFileType(Path filePath) throws IOException {
    Metadata metadata = new Metadata();
    metadata.set(TikaCoreProperties.RESOURCE_NAME_KEY, filePath.toFile().getName());
    try (TikaInputStream stream = TikaInputStream.get(filePath, metadata)) {
      var mediaType = detector.detect(stream, metadata);
      return mediaType.toString();
    }
  }
}
