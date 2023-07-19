/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import org.jetbrains.annotations.NotNull;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DockerImageName {

  private static final Pattern tagPattern = Pattern.compile("^(.+?)(?::([^:/]+))?$");

  @NotNull
  private static Matcher matchImageName(String imageName) {
    if (imageName.contains("@sha256")) {
      String[] digestParts = imageName.split("@");
      imageName = digestParts[0];
      // digest = digestParts[1];
    }

    var matcher = tagPattern.matcher(imageName);
    if (!matcher.matches()) {
      throw new IllegalArgumentException(
          "Parsing image name failed. It was not properly formatted image name: "
              + imageName
              + " Image name format is usually [registryAddress/]name:tag. See docker or OCI"
              + " standard documentation for more details.");
    }
    return matcher;
  }

  /**
   * See https://github.com/distribution/distribution/blob/main/reference/regexp.go#L72 and
   * https://docs.docker.com/engine/reference/commandline/pull/#pull-an-image-by-digest-immutable-identifier
   *
   * @param imageName the full image name.
   * @return the tag
   */
  public static String getTag(String imageName) {
    var tag = matchImageName(imageName).group(2);
    return tag != null ? tag : "latest";
  }

  /**
   * Extracts the image path from a given container URL.
   *
   * The method takes a container URL string in the format [hostName]/[imagePath]:[tag] and returns
   * the image path. This includes the namespace and image name but excludes the host and the tag.
   * If no tag is present in the URL, the method will return the full image path.
   *
   * @param containerURL A string representing the container URL. Should be in the format [hostName]/[imageName]:[tag].
   * @return A string representing the image path (i.e., namespace and image name) from the container URL.
   */
  public static String getImagePath(String containerURL) {
    String imageName = containerURL;

    var firstSlash = containerURL.indexOf('/');
    if (firstSlash >= 0) {
      imageName = containerURL.substring(firstSlash + 1, containerURL.length());
    }

    var lastColon = imageName.lastIndexOf(':');
    if (lastColon >= 0) {
      imageName = imageName.substring(0, lastColon);
    }
    return imageName;
  }

  /**
   * Updates the image name with the new tag
   *
   * @param imageName the update name to update
   * @param newTag the new tag to set
   * @return the updated image name
   */
  public static String updateImageWithTag(String imageName, String newTag) {
    var matcher = matchImageName(imageName);
    return matcher.group(1) + ":" + newTag;
  }
}
