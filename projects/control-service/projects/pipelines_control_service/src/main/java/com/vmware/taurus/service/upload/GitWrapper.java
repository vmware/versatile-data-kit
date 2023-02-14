/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.vmware.taurus.exception.Bug;
import com.vmware.taurus.exception.ExternalSystemError;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.eclipse.jgit.api.*;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.transport.CredentialsProvider;
import org.eclipse.jgit.transport.PushResult;
import org.eclipse.jgit.transport.RemoteRefUpdate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * Wrapper which eases the usage of JGit and is used in {@link JobUpload} to operate on the
 * repository data jobs repository.
 *
 * <p>TODO: transform into a full facade by handling git object internally
 */
@Component
@Slf4j
public class GitWrapper {

  @FunctionalInterface
  interface PrePushOperation {
    void apply() throws IOException, GitAPIException;
  }

  private static final String COMMIT_TEMPLATE_SIGNED =
      "Update data job: %s\n\n%s\n\nSigned-off-by: %s";

  private static final String COMMIT_TEMPLATE_UNSIGNED = "Update data job: %s\n\n%s";

  private static final String FILE_PATTERN = ".";

  private static final String REPOSITORY = "data-jobs";

  private final String gitDataJobsUrl;

  private final String gitDataJobsBranch;

  private final String gitDataJobsRemote;

  public GitWrapper(
      @Value("${datajobs.git.url}") String gitDataJobsUrl,
      @Value("${datajobs.git.branch}") String gitDataJobsBranch,
      @Value("${datajobs.git.remote}") String gitDataJobsRemote,
      @Value("${datajobs.git.ssl.enabled}") boolean gitDataJobsSslEnabled) {

    this.gitDataJobsUrl = constructCorrectGitUrl(gitDataJobsUrl, gitDataJobsSslEnabled);
    this.gitDataJobsBranch = gitDataJobsBranch;
    this.gitDataJobsRemote = gitDataJobsRemote;
  }

  public Git cloneJobRepository(File tempDirPath, CredentialsProvider credentialsProvider)
      throws GitAPIException {
    // TODO: optimise to not clone the whole repository for every upload endpoint, but rather
    //  reuse the same repository but updating the a single job file:
    //
    // https://stackoverflow.com/questions/600079/how-do-i-clone-a-subdirectory-only-of-a-git-repository/52269934#52269934
    File jobsRepository = new File(tempDirPath, REPOSITORY);
    return Git.cloneRepository()
        .setURI(gitDataJobsUrl)
        .setBranch(gitDataJobsBranch)
        .setRemote(gitDataJobsRemote)
        .setDirectory(jobsRepository)
        .setCredentialsProvider(credentialsProvider)
        .call();
  }

  public String pushCreateJob(
      Git git,
      String jobName,
      CredentialsProvider credentialsProvider,
      String username,
      String reason,
      File newJobDir)
      throws GitAPIException, IOException {
    pushChanges(
        git,
        jobName,
        credentialsProvider,
        username,
        reason,
        () -> updateDataJobDirectory(git, jobName, newJobDir));
    return getLatestCommitSHAFile(git, jobName);
  }

  private void pushChanges(
      Git git,
      String jobName,
      CredentialsProvider credentialsProvider,
      String username,
      String reason,
      PrePushOperation op)
      throws IOException, GitAPIException {
    op.apply();
    Status gitStatus = git.status().call();
    // if no changes are introduced, no point in try to push we skip
    if (gitStatus.hasUncommittedChanges()) {
      commitChanges(git, username, jobName, reason);
      while (tryToPush(git.push().setCredentialsProvider(credentialsProvider))) {
        revertAndPullRemote(git, credentialsProvider);
        op.apply();
        gitStatus = git.status().call();
        if (gitStatus.hasUncommittedChanges()) {
          commitChanges(git, username, jobName, reason);
        } else {
          break;
        }
      }
    }
  }

  public void pushDeleteJob(
      Git git,
      String jobName,
      CredentialsProvider credentialsProvider,
      String username,
      String reason)
      throws IOException, GitAPIException {
    pushChanges(
        git,
        jobName,
        credentialsProvider,
        username,
        reason,
        () -> deleteDataJobFromDirectory(git, jobName));
  }

  public File getDataJobDirectory(Git git, String jobName) {
    File repositoryLocation = git.getRepository().getDirectory().getParentFile();
    var jobRepositoryFolderJobPath = new File(repositoryLocation, jobName);
    if (jobRepositoryFolderJobPath.getAbsolutePath().equals(repositoryLocation.getAbsolutePath())) {
      throw new Bug(
          "Trying to get the full repo folder for a single job. " + "That should not be possible.",
          null);
    }
    return jobRepositoryFolderJobPath;
  }

  private boolean tryToPush(PushCommand push) throws GitAPIException {
    log.debug(
        "Try to push: repo: {} remote: {} ref: {} with options {}",
        push.getRepository(),
        push.getRemote(),
        push.getRefSpecs(),
        push.getPushOptions());
    Iterator<PushResult> pushResults = push.setForce(false).call().iterator();
    return verifyFailedPush(pushResults);
  }

  public void gitAdd(Git git) throws GitAPIException {
    git.add().addFilepattern(FILE_PATTERN).call();
    git.add().addFilepattern(FILE_PATTERN).setUpdate(true).call();
  }

  public static String constructCorrectGitUrl(
      String gitDataJobsUrl, boolean gitDataJobsSslEnabled) {
    URI u = URI.create(gitDataJobsUrl);
    if (StringUtils.isBlank(u.getScheme())) {
      String scheme = gitDataJobsSslEnabled ? "https" : "http";
      return scheme + "://" + u.toString();
    }
    return gitDataJobsUrl;
  }

  private void revertAndPullRemote(Git git, CredentialsProvider credentialsProvider)
      throws GitAPIException {
    // This removes the latest commit with the new data job to reset the branch to remote in
    // order to have a clean fast forward pull from remote with no conflicts. We can't pull
    // with rebase as there might be conflicts which can be resolve with merge strategies,
    // but they don't work properly.
    log.debug(
        "Revert local change and reset to {}/{} in order to try to push again",
        gitDataJobsRemote,
        gitDataJobsBranch);
    git.reset().setRef("HEAD~1").setMode(ResetCommand.ResetType.HARD).call();
    git.pull().setCredentialsProvider(credentialsProvider).call();
  }

  private void updateDataJobDirectory(Git git, String jobName, File newJobDir)
      throws IOException, GitAPIException {
    log.debug("Add job {} content directory to local git", jobName);
    File repositoryLocation = git.getRepository().getDirectory().getParentFile();
    var jobRepositoryFolderJobPath = new File(repositoryLocation, jobName);
    if (jobRepositoryFolderJobPath.getAbsolutePath().equals(repositoryLocation.getAbsolutePath())) {
      throw new Bug(
          "Trying to delete the full repo folder when deploying job. "
              + "That should not be possible.",
          null);
    }
    org.apache.commons.io.FileUtils.deleteDirectory(jobRepositoryFolderJobPath);
    org.apache.commons.io.FileUtils.copyDirectory(newJobDir, jobRepositoryFolderJobPath);
    gitAdd(git);
  }

  private void deleteDataJobFromDirectory(Git git, String jobName)
      throws IOException, GitAPIException {
    File repositoryLocation = git.getRepository().getDirectory().getParentFile();
    var jobRepositoryFolderJobPath = new File(repositoryLocation, jobName);
    if (jobRepositoryFolderJobPath.getAbsolutePath().equals(repositoryLocation.getAbsolutePath())) {
      throw new Bug(
          "Trying to delete the full repo folder when deploying job. "
              + "That should not be possible.",
          null);
    }
    org.apache.commons.io.FileUtils.deleteDirectory(jobRepositoryFolderJobPath);
    gitAdd(git);
  }

  /**
   * @return true if push has failed and should be retried. If it's succesful it returns false. If
   *     there's unrecoverable issue - throws an error.
   */
  private boolean verifyFailedPush(Iterator<PushResult> pushResults) {
    if (pushResults.hasNext()) {
      while (pushResults.hasNext()) {
        PushResult result = pushResults.next();
        log.debug("Verify if the push has passed: {}", ToStringBuilder.reflectionToString(result));
        ArrayList<RemoteRefUpdate> updates = new ArrayList<>(result.getRemoteUpdates());
        for (RemoteRefUpdate refUpdate : updates) {
          RemoteRefUpdate.Status status = refUpdate.getStatus();
          switch (status) {
            case REJECTED_NONFASTFORWARD:
            case NOT_ATTEMPTED:
            case REJECTED_REMOTE_CHANGED:
            case AWAITING_REPORT:
              return true; // we failed but we should retry
            case NON_EXISTING:
            case REJECTED_NODELETE:
            case REJECTED_OTHER_REASON:
              throw new ExternalSystemError(
                  ExternalSystemError.MainExternalSystem.GIT,
                  String.format(
                      "We failed to push successfully source for data job. "
                          + "Failure status is %s, message: %s: .",
                      refUpdate.getStatus().toString(), refUpdate.getMessage()));
            case OK:
            case UP_TO_DATE:
              return false; // we did not fail - aka we succeeded. Yay.

            default:
              throw new ExternalSystemError(
                  ExternalSystemError.MainExternalSystem.GIT,
                  String.format(
                      "We failed to push successfully source for data job. Remote git return"
                          + " unknown status: Failure status is %s, message: %s: .",
                      refUpdate.getStatus().toString(), refUpdate.getMessage()));
          }
        }
      }
    }
    return false;
  }

  RevCommit commitChanges(Git git, String username, String jobName, String reason)
      throws GitAPIException {
    log.debug("Commit changes to job {} on behalf of {} to local git", jobName, username);
    RevCommit commit;
    if (StringUtils.isBlank(reason)) {
      reason = "Updating data job: " + jobName;
    }
    if (StringUtils.isBlank(username)) {
      String commitMessage = String.format(COMMIT_TEMPLATE_UNSIGNED, jobName, reason);
      commit = git.commit().setMessage(commitMessage).call();
    } else {
      String commitMessage = String.format(COMMIT_TEMPLATE_SIGNED, jobName, reason, username);
      commit = git.commit().setMessage(commitMessage).setAuthor(username, "").call();
    }
    return commit;
  }

  String getLatestCommitSHAFile(Git git, String fileName) throws GitAPIException {
    RevCommit latestCommit = null;
    Iterator<RevCommit> commits;
    LogCommand log = git.log();
    if (fileName != null) {
      log = log.addPath(fileName);
    }
    commits = log.call().iterator();
    if (commits.hasNext()) {
      latestCommit = commits.next();
    }
    return latestCommit != null ? latestCommit.name() : null;
  }

  String getLatestCommitSHARepository(Git git) throws GitAPIException {
    return getLatestCommitSHAFile(git, null);
  }
}
