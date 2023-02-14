/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import com.vmware.taurus.exception.ExternalSystemError;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.transport.CredentialsProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.util.Optional;

/**
 * Class responsible for handling the data job archive coming from the client. The main
 * functionality of the class is to hadnle the archive binary containing the data job using {@link
 * FileUtils} and push the data job to the data jobs repository using {@link GitWrapper}.
 */
@Service
public class JobUpload {

  private static final Logger log = LoggerFactory.getLogger(JobUpload.class);

  private final String datajobsTempStorageFolder;
  private final GitCredentialsProvider gitCredentialsProvider;
  private final GitWrapper gitWrapper;
  private final FeatureFlags featureFlags;
  private final AuthorizationProvider authorizationProvider;
  private final JobUploadValidator jobUploadValidator;

  @Autowired
  public JobUpload(
      @Value("${datajobs.temp.storage.folder:}") String datajobsTempStorageFolder,
      GitCredentialsProvider gitCredentialsProvider,
      GitWrapper gitWrapper,
      FeatureFlags featureFlags,
      AuthorizationProvider authorizationProvider,
      JobUploadValidator jobUploadValidator) {
    this.datajobsTempStorageFolder = datajobsTempStorageFolder;
    this.gitCredentialsProvider = gitCredentialsProvider;
    this.gitWrapper = gitWrapper;
    this.featureFlags = featureFlags;
    this.authorizationProvider = authorizationProvider;
    this.jobUploadValidator = jobUploadValidator;
  }

  /**
   * Get data job source as a zip file.
   *
   * @param jobName the data job whose source it will get
   * @return resource containing data job content in a zip format.
   */
  public Optional<Resource> getDataJob(String jobName) {
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try (var tempDirPath =
        new EphemeralFile(datajobsTempStorageFolder, jobName, "get data job source")) {
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
    String jobVersion;
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try (var tempDirPath = new EphemeralFile(datajobsTempStorageFolder, jobName, "deploy")) {
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
    CredentialsProvider credentialsProvider = gitCredentialsProvider.getProvider();
    try (var tempDirPath = new EphemeralFile(datajobsTempStorageFolder, jobName, "delete")) {
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
