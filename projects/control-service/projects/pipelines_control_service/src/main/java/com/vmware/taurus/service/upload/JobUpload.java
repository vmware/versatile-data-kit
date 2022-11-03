/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.exception.ErrorMessage;
import com.vmware.taurus.exception.ExternalSystemError;
import lombok.AllArgsConstructor;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.transport.CredentialsProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Class responsible for handling the data job archive coming from the client. The main
 * functionality of the class is to hadnle the archive binary containing the data job using {@link
 * FileUtils} and push the data job to the data jobs repository using {@link GitWrapper}.
 */
@Service
@AllArgsConstructor
public class JobUpload {

  private static final Logger log = LoggerFactory.getLogger(JobUpload.class);

  private static final String TEMPORARY_DIRECTORY_PREFIX = "job_";

  @Autowired private final GitCredentialsProvider gitCredentialsProvider;

  @Autowired private final GitWrapper gitWrapper;

  @Autowired private final FeatureFlags featureFlags;

  @Autowired private final AuthorizationProvider authorizationProvider;

  @Autowired private final JobUploadValidator jobUploadValidator;

  /**
   * Get data job source as a zip file.
   *
   * @param jobName the data job whose source it will get
   * @return resource containing data job content in a zip format.
   */
  public Optional<Resource> getDataJob(String jobName) {
    Path tempDirPath = null;
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try {
      tempDirPath = FileUtils.createTempDir(TEMPORARY_DIRECTORY_PREFIX);

      Git git =
          gitWrapper.cloneJobRepository(
              new File(tempDirPath.toFile(), "repo"), credentialsProvider);
      File jobDirectory = gitWrapper.getDataJobDirectory(git, jobName);
      if (jobDirectory.isDirectory()) {
        File tempFile = File.createTempFile(jobName, "zip");
        tempFile.delete();
        FileUtils.zipDataJob(jobDirectory, tempFile);
        return Optional.of(new FileUtils.CleanupFileInputStreamResource(tempFile));
      } else {
        return Optional.empty();
      }

    } catch (GitAPIException e) {
      // TODO: split into 5xx and 4xx errors depending on exception (e.g too big upload is client
      // error and not server error)
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.GIT,
          String.format(
              "Communication with the git server failed while trying to get data job source: %s. "
                  + "Please read the exception and follow the instructions.",
              jobName),
          e);
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format(
              "Operations on the file system failed while trying to get data job source: %s",
              jobName),
          e);
    } finally {
      if (tempDirPath != null) {
        try {
          FileUtils.removeDir(tempDirPath);
        } catch (IOException e) {
          log.warn(
              new ErrorMessage(
                      String.format(
                          "Unable to clean up temporary files while tyring to get data job source:"
                              + " %s",
                          jobName),
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
  }

  /**
   * Public data job to remote git repository and return its version (git version)
   *
   * @param jobName - the data job name
   * @param resource - the data job source as a zip file.
   * @param reason - reason specified by user for publishing the data job
   * @return the new version (commit hash) of the data job. If there are not changes it will return
   *     the latest version (commit) of the data job.
   */
  public String publishDataJob(String jobName, Resource resource, String reason) {
    log.debug("Publish datajob to git {}", jobName);
    Path tempDirPath = null;
    String jobVersion;
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try {
      tempDirPath = FileUtils.createTempDir(TEMPORARY_DIRECTORY_PREFIX);

      File jobFolder =
          FileUtils.unzipDataJob(resource, new File(tempDirPath.toFile(), "job"), jobName);
      jobUploadValidator.validateJob(jobName, jobFolder.toPath());

      Git git =
          gitWrapper.cloneJobRepository(
              new File(tempDirPath.toFile(), "repo"), credentialsProvider);

      jobVersion = createRemoteJob(git, jobName, credentialsProvider, reason, jobFolder);
    } catch (GitAPIException e) {
      // TODO: split into 5xx and 4xx errors depending on exception (e.g too big upload is client
      // error and not server error)
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.GIT,
          String.format(
              "Communication with the git server failed while trying to deploy data job: %s. "
                  + "Please read the exception and follow the instructions.",
              jobName),
          e);
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format(
              "Operations on the file system failed while trying to handle deployment of job: %s",
              jobName),
          e);
    } finally {
      if (tempDirPath != null) {
        try {
          // TODO: go with try with resources:
          //
          // https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html#:~:text=Note%3A%20A%20try%20%2Dwith%2D,resources%20declared%20have%20been%20closed.
          FileUtils.removeDir(tempDirPath);
        } catch (IOException e) {
          log.warn(
              new ErrorMessage(
                      String.format(
                          "Unable to clean up temporary files while tyring to deploy: %s", jobName),
                      String.format("Error: %s", e.getMessage()),
                      "Job is successfully deployed, but temporary files are left on the file"
                          + " system.",
                      "Contact the provider to resolve the issue or clean up the temporary files"
                          + " manually.")
                  .toString(),
              e);
        }
      }
    }
    return jobVersion;
  }

  /**
   * Delete the data job source directory.
   *
   * @param jobName the data job name
   * @param reason reason specified by user for deleting the data job
   */
  public void deleteDataJob(String jobName, String reason) {
    Path tempDirPath = null;
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try {
      tempDirPath = FileUtils.createTempDir(TEMPORARY_DIRECTORY_PREFIX);

      Git git =
          gitWrapper.cloneJobRepository(
              new File(tempDirPath.toFile(), "repo"), credentialsProvider);

      removeRemoteJob(git, jobName, credentialsProvider, reason);
    } catch (GitAPIException e) {
      // TODO: split into 5xx and 4xx errors depending on exception (e.g too big upload is client
      // error and not server error)
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.GIT,
          String.format(
              "Communication with the git server failed while trying to delete data job: %s. "
                  + "Please read the exception and follow the instructions.",
              jobName),
          e);
    } catch (IOException e) {
      throw new ExternalSystemError(
          ExternalSystemError.MainExternalSystem.HOST_CONTAINER,
          String.format(
              "Operations on the file system failed while trying to handle deletion of job: %s",
              jobName),
          e);
    } finally {
      if (tempDirPath != null) {
        try {
          // TODO: go with try with resources:
          //
          // https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html#:~:text=Note%3A%20A%20try%20%2Dwith%2D,resources%20declared%20have%20been%20closed.
          FileUtils.removeDir(tempDirPath);
        } catch (IOException e) {
          log.warn(
              new ErrorMessage(
                      String.format(
                          "Unable to clean up temporary files while tyring to delete: %s", jobName),
                      String.format("Error: %s", e.getMessage()),
                      "Job is successfully deleted, but temporary files are left on the file"
                          + " system.",
                      "Contact the provider to resolve the issue or clean up the temporary files"
                          + " manually.")
                  .toString(),
              e);
        }
      }
    }
  }

  private String createRemoteJob(
      Git git,
      String jobName,
      CredentialsProvider credentialsProvider,
      String reason,
      File jobFolder)
      throws GitAPIException, IOException {
    String userID = null;
    if (featureFlags.isSecurityEnabled()) {
      Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
      userID = authorizationProvider.getUserId(authentication);
    }
    return gitWrapper.pushCreateJob(git, jobName, credentialsProvider, userID, reason, jobFolder);
  }

  private void removeRemoteJob(
      Git git, String jobName, CredentialsProvider credentialsProvider, String reason)
      throws GitAPIException, IOException {
    String userID = null;
    if (featureFlags.isSecurityEnabled()) {
      Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
      userID = authorizationProvider.getUserId(authentication);
    }
    gitWrapper.pushDeleteJob(git, jobName, credentialsProvider, userID, reason);
  }
}
