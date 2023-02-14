/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import com.google.common.io.Files;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.ResetCommand;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.transport.CredentialsProvider;
import org.eclipse.jgit.transport.URIish;
import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class GitWrapperTest {

  private CredentialsProvider credentialsProvider;

  private GitWrapper gitWrapper;

  private File localRepositoryMock;

  private Git git;

  private File secondLocalRepositoryMock;

  private Git secondGit;

  private File thirdLocalRepositoryMock;

  private Git thirdGit;

  private File remoteRepositoryMock;

  private Git remoteGit;

  @BeforeEach
  public void setup() throws Exception {
    localRepositoryMock = Files.createTempDir();
    remoteRepositoryMock = Files.createTempDir();
    secondLocalRepositoryMock = Files.createTempDir();
    thirdLocalRepositoryMock = Files.createTempDir();

    git = Git.init().setDirectory(localRepositoryMock).call();
    git.commit().setMessage("Initial commit").call();

    secondGit = Git.init().setDirectory(secondLocalRepositoryMock).call();
    secondGit.commit().setMessage("Initial commit").call();

    thirdGit = Git.init().setDirectory(thirdLocalRepositoryMock).call();
    thirdGit.commit().setMessage("Initial commit").call();

    remoteGit = Git.init().setDirectory(remoteRepositoryMock).call();

    Git.init().setDirectory(remoteRepositoryMock).call();
    URIish repoURI = new URIish().setPath(remoteRepositoryMock.getPath());

    git.remoteAdd().setUri(repoURI).setName("origin").call();

    secondGit.remoteAdd().setUri(repoURI).setName("origin").call();

    thirdGit.remoteAdd().setUri(repoURI).setName("origin").call();

    gitWrapper = new GitWrapper("", "", "", true);

    credentialsProvider =
        new UsernamePasswordCredentialsProvider("example-user", "example-password");
  }

  @AfterEach
  public void cleanup() {
    localRepositoryMock.delete();
    secondLocalRepositoryMock.delete();
    thirdLocalRepositoryMock.delete();
    remoteRepositoryMock.delete();
  }

  @Test
  public void testAddFileNoException() throws IOException {
    File file = new File(localRepositoryMock, "example");
    file.createNewFile();

    Assertions.assertDoesNotThrow(() -> gitWrapper.gitAdd(git));
  }

  @Test
  public void testCommitChanges() throws GitAPIException {
    RevCommit commit = gitWrapper.commitChanges(git, "user", "example-job", "example-reason");

    Assertions.assertEquals("user", commit.getAuthorIdent().getName());
    Assertions.assertEquals("", commit.getAuthorIdent().getEmailAddress());
    Assertions.assertTrue(commit.getFullMessage().contains("user"));
    Assertions.assertTrue(commit.getFullMessage().contains("example-job"));
    Assertions.assertTrue(commit.getFullMessage().contains("example-reason"));
  }

  @Test
  public void testFileCommitSha() throws GitAPIException, IOException {
    new File(localRepositoryMock, "example").createNewFile();
    gitWrapper.gitAdd(git);
    gitWrapper.commitChanges(git, "user", "example-job", "example-reason");

    String fileLatestCommitSha = gitWrapper.getLatestCommitSHAFile(git, "example");

    Assertions.assertFalse(StringUtils.isBlank(fileLatestCommitSha));
  }

  @Test
  public void testRepoCommitSha() throws GitAPIException {
    String repoLatestCommitSha = gitWrapper.getLatestCommitSHARepository(git);

    Assertions.assertFalse(StringUtils.isBlank(repoLatestCommitSha));
  }

  @Test
  public void testCommitWithNoUsername() throws GitAPIException, IOException {
    File file = new File(localRepositoryMock, "example-job-1");
    file.createNewFile();
    RevCommit commit = gitWrapper.commitChanges(git, null, "example-job-1", "example-reason");

    Assertions.assertTrue(commit.getFullMessage().contains("example-job-1"));
  }

  @Test
  public void testPushInvalid(@TempDir Path tempDir)
      throws GitAPIException, IOException, URISyntaxException {
    URIish repoURI = new URIish("git@foo:bar.git");
    git.remoteAdd().setUri(repoURI).setName("origin").call();

    new File(tempDir.toFile(), "05_query.py").createNewFile();
    FileUtils.copyDirectoryToDirectory(tempDir.toFile(), localRepositoryMock);

    gitWrapper.gitAdd(git);

    Assertions.assertThrows(
        Exception.class,
        () ->
            gitWrapper.pushCreateJob(
                git, "example-job-1", credentialsProvider, "example-user", null, tempDir.toFile()));
  }

  @Test
  public void testConcurrentPushes() throws GitAPIException, IOException {
    String pushedCommitSHA;
    String latestCommitSHARepo;
    String latestCommitSHAFile;

    File jobsBaseFolder1 = Files.createTempDir();

    File jobFolder1 = new File(jobsBaseFolder1.getPath(), "example-job-1");
    jobFolder1.mkdir();

    File file1 = new File(jobFolder1, "05_query.py");
    file1.createNewFile();
    FileUtils.writeStringToFile(file1, "1", Charset.defaultCharset());

    FileUtils.copyDirectoryToDirectory(jobFolder1, localRepositoryMock);

    gitWrapper.gitAdd(git);

    pushedCommitSHA =
        gitWrapper.pushCreateJob(
            git, "example-job-1", credentialsProvider, "example-user", null, jobFolder1);
    latestCommitSHARepo = gitWrapper.getLatestCommitSHARepository(git);
    latestCommitSHAFile = gitWrapper.getLatestCommitSHAFile(git, "example-job-1");

    remoteGit.reset().setMode(ResetCommand.ResetType.HARD).call();

    File remoteFolder1 = new File(remoteRepositoryMock, jobFolder1.getName());
    File remoteFileContent1 = new File(remoteFolder1, remoteFolder1.list()[0]);
    Assertions.assertTrue(remoteFolder1.exists());
    Assertions.assertTrue(remoteFileContent1.exists());
    Assertions.assertEquals(
        "1", FileUtils.readFileToString(remoteFileContent1, Charset.defaultCharset()));
    Assertions.assertEquals(
        "1", FileUtils.readFileToString(remoteFileContent1, Charset.defaultCharset()));
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHARepo);
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHAFile);
    var firstPushCommits =
        StreamSupport.stream(remoteGit.log().call().spliterator(), false)
            .collect(Collectors.toList());
    Assertions.assertEquals(2, firstPushCommits.size());

    File jobFolder2 = new File(jobsBaseFolder1.getPath(), "example-job-2");
    jobFolder2.mkdir();

    File file2 = new File(jobFolder2, "05_query.py");
    file2.createNewFile();
    FileUtils.writeStringToFile(file2, "2", Charset.defaultCharset());

    FileUtils.copyDirectoryToDirectory(jobFolder2, secondLocalRepositoryMock);

    gitWrapper.gitAdd(secondGit);
    pushedCommitSHA =
        gitWrapper.pushCreateJob(
            secondGit, "example-job-2", credentialsProvider, "example-user", null, jobFolder2);
    latestCommitSHARepo = gitWrapper.getLatestCommitSHARepository(secondGit);
    latestCommitSHAFile = gitWrapper.getLatestCommitSHAFile(secondGit, "example-job-2");

    remoteGit.reset().setMode(ResetCommand.ResetType.HARD).setRef("HEAD").call();
    File remoteFile2 = new File(remoteRepositoryMock, jobFolder2.getName());
    File remoteFileContent2 = new File(remoteFile2, remoteFile2.list()[0]);
    Assertions.assertTrue(remoteFile2.exists());
    Assertions.assertEquals(
        "2", FileUtils.readFileToString(remoteFileContent2, Charset.defaultCharset()));
    Assertions.assertTrue(remoteFolder1.exists());
    Assertions.assertEquals(
        "1", FileUtils.readFileToString(remoteFileContent1, Charset.defaultCharset()));
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHARepo);
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHAFile);
    List<RevCommit> secondPushCommits =
        StreamSupport.stream(remoteGit.log().call().spliterator(), false)
            .collect(Collectors.toList());
    Assertions.assertEquals(3, secondPushCommits.size());

    File jobsBaseFolder2 = Files.createTempDir();

    File jobFolder3 = new File(jobsBaseFolder2.getPath(), "example-job-1");
    jobFolder3.mkdir();

    File file3 = new File(jobFolder3, "05_query.py");
    file3.createNewFile();
    FileUtils.writeStringToFile(file3, "3", Charset.defaultCharset());

    FileUtils.copyDirectoryToDirectory(jobFolder3, thirdLocalRepositoryMock);

    gitWrapper.gitAdd(thirdGit);
    pushedCommitSHA =
        gitWrapper.pushCreateJob(
            thirdGit, "example-job-1", credentialsProvider, "example-user", null, jobFolder3);
    latestCommitSHARepo = gitWrapper.getLatestCommitSHARepository(thirdGit);
    latestCommitSHAFile = gitWrapper.getLatestCommitSHAFile(thirdGit, "example-job-1");

    remoteGit.reset().setMode(ResetCommand.ResetType.HARD).call();
    Assertions.assertTrue(remoteFile2.exists());
    Assertions.assertEquals(
        "2", FileUtils.readFileToString(remoteFileContent2, Charset.defaultCharset()));
    Assertions.assertTrue(remoteFolder1.exists());
    Assertions.assertEquals(
        "3", FileUtils.readFileToString(remoteFileContent1, Charset.defaultCharset()));
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHARepo);
    Assertions.assertEquals(pushedCommitSHA, latestCommitSHAFile);

    gitWrapper.pushDeleteJob(secondGit, "example-job-2", credentialsProvider, "example-user", null);
    remoteGit.reset().setMode(ResetCommand.ResetType.HARD).setRef("HEAD").call();
    File remoteJobFolder2 = new File(remoteRepositoryMock, "example-job-2");
    Assertions.assertFalse(remoteJobFolder2.exists());

    var remoteCommits =
        StreamSupport.stream(remoteGit.log().call().spliterator(), false)
            .collect(Collectors.toList());
    ;
    Assertions.assertEquals(5, remoteCommits.size());
  }
}
