/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import static com.vmware.taurus.service.upload.FileUtils.createTempDir;

import com.google.common.collect.Iterables;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.TestIOUtils;
import com.vmware.taurus.authorization.provider.AuthorizationProvider;
import com.vmware.taurus.base.FeatureFlags;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Optional;
import net.lingala.zip4j.ZipFile;
import net.lingala.zip4j.exception.ZipException;
import net.lingala.zip4j.model.ZipParameters;
import org.apache.commons.io.FileUtils;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.ResetCommand;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.revwalk.RevCommit;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;

@ExtendWith(MockitoExtension.class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobUploadTest {

  File remoteRepositoryDir;
  private Git remoteGit;

  @Mock private GitCredentialsProvider gitCredentialsProvider;

  private GitWrapper gitWrapper;

  @Mock private FeatureFlags featureFlags;

  @Mock private AuthorizationProvider authorizationProvider;

  @Mock private JobUploadValidator jobUploadValidator;

  @Mock private JobUploadFileFilter jobUploadFileFilter;

  private JobUpload jobUpload;

  @Value("${datajobs.git.branch}")
  public String gitDataJobsBranch;

  @Value("${datajobs.git.remote}")
  public String gitDataJobsRemote;

  @BeforeEach
  public void setup() throws GitAPIException, IOException {
    remoteRepositoryDir = Files.createTempDirectory("remote_repo").toFile();
    remoteGit = Git.init().setDirectory(remoteRepositoryDir).call();
    gitWrapper =
        new GitWrapper(
            "file://" + remoteRepositoryDir.getAbsolutePath(),
            gitDataJobsBranch,
            gitDataJobsRemote,
            true);

    jobUpload =
        new JobUpload(
            null,
            gitCredentialsProvider,
            gitWrapper,
            featureFlags,
            authorizationProvider,
            jobUploadValidator,
            jobUploadFileFilter);
  }

  @AfterEach
  public void cleanup() {
    remoteRepositoryDir.delete();
  }

  @Test
  public void testPushNoAuthentication() throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(false);

    Resource jobResource = new ClassPathResource("/file_test/test_job.zip");

    jobUpload.publishDataJob("example", jobResource, "example-reason");

    refreshRemoteGitDirectoryWithLatestChanges();
    Assertions.assertTrue(new File(this.remoteRepositoryDir, "example").isDirectory());
  }

  @Test
  public void testPushAuthentication() throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);

    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    Resource jobResource = new ClassPathResource("/file_test/test_job.zip");

    jobUpload.publishDataJob("example", jobResource, "example-reason");

    refreshRemoteGitDirectoryWithLatestChanges();
    Assertions.assertTrue(new File(this.remoteRepositoryDir, "example").isDirectory());

    var commits = Iterables.toArray(remoteGit.log().call(), RevCommit.class);
    Assertions.assertEquals(1, commits.length);
    Assertions.assertEquals("user", commits[0].getAuthorIdent().getName());
  }

  private void refreshRemoteGitDirectoryWithLatestChanges() throws GitAPIException {
    remoteGit.reset().setMode(ResetCommand.ResetType.HARD).call();
  }

  @Test
  public void testWithSecondUploadNoChanges(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    File jobDir = mkdir(tempDir.toFile(), "job_dir");
    writeToFile(jobDir, "file.txt", "11");

    File zipFile = createZipFromDir(jobDir, new File(tempDir.toFile(), "some.zip"));
    String firstUploadVersion =
        jobUpload.publishDataJob("job-name", new FileSystemResource(zipFile), "commit 1");
    // put unrelated commit between the two updates to verify commit return is of original job
    jobUpload.publishDataJob(
        "other-unrelated-job", new FileSystemResource(zipFile), "commit unrelated");
    String secondUploadVersion =
        jobUpload.publishDataJob("job-name", new FileSystemResource(zipFile), "commit 2");
    // second version should be same as first as no changes are present in the job content
    Assertions.assertEquals(firstUploadVersion, secondUploadVersion);
  }

  @Test
  public void testWithEmptyJobDirectory(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    File jobDir = mkdir(tempDir.toFile(), "job_dir");
    File jobFile = writeToFile(jobDir, "file.txt", "11");

    File zipFile = createZipFromDir(jobDir, new File(tempDir.toFile(), "not_empty.zip"));
    jobUpload.publishDataJob("job-name", new FileSystemResource(zipFile), "commit 1");

    jobFile.delete();
    zipFile = createZipFromDir(jobDir, new File(tempDir.toFile(), "empty.zip"));
    jobUpload.publishDataJob("job-name", new FileSystemResource(zipFile), "commit 1");

    Assertions.assertFalse(new File(remoteRepositoryDir, "job-name").exists());
  }

  /**
   * If zip is foo/job-name/file.txt foo/job-name/nested_dir/file2.txt then data job dir uploaded
   * will look like job-name/job-name/file.txt job-name/job-name/nested_dir/file2.txt
   */
  @Test
  public void testWithRootFolderNameInZip(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    File parentDir = mkdir(tempDir.toFile(), "foo");
    File jobDir = mkdir(parentDir, "job-name");
    writeToFile(jobDir, "file.txt", "11");

    File zipFile =
        createZipFromDirWithRootFolderNameInZip(jobDir, new File(tempDir.toFile(), "whatever.zip"));
    jobUpload.publishDataJob("job-name", new FileSystemResource(zipFile), "commit 1");

    refreshRemoteGitDirectoryWithLatestChanges();
    TestIOUtils.compareDirectories(parentDir, new File(remoteRepositoryDir, "job-name"));
  }

  @Test
  public void testPushMultipleCommits(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    File jobDir = mkdir(tempDir.toFile(), "data-jobs-example");
    File nestedDir = mkdir(jobDir, "nested_dir");

    File nestedDirFile = writeToFile(nestedDir, "file_nested_dir.txt", "11");
    File nestedDirFileToDelete = writeToFile(nestedDir, "file_nested_dir_delete.txt", "11");
    File fileToRemain = writeToFile(jobDir, "file_to_remain.txt", "11");
    File fileToDelete = writeToFile(jobDir, "file_to_delete.txt", "11");
    File fileToChange = writeToFile(jobDir, "file_to_change.txt", "11");

    File zipFile = createZipFromDir(jobDir, new File(tempDir.toFile(), "example.zip"));
    jobUpload.publishDataJob("example", new FileSystemResource(zipFile), "commit 1");

    refreshRemoteGitDirectoryWithLatestChanges();
    TestIOUtils.compareDirectories(jobDir, new File(remoteRepositoryDir, "example"));

    nestedDirFileToDelete.delete();
    fileToDelete.delete();
    writeToFile(jobDir, fileToChange.getName(), "22");

    zipFile.delete();
    zipFile = createZipFromDir(jobDir, new File(tempDir.toFile(), "example.zip"));
    String jobCommit =
        jobUpload.publishDataJob("example", new FileSystemResource(zipFile), "commit 2");

    refreshRemoteGitDirectoryWithLatestChanges();
    Assertions.assertEquals(remoteGit.log().call().iterator().next().getName(), jobCommit);
    TestIOUtils.compareDirectories(jobDir, new File(remoteRepositoryDir, "example"));
  }

  @Test
  public void testDeleteDataJob(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);

    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    Resource jobResource =
        new ClassPathResource("/file_test/test_job.zip", this.getClass().getClassLoader());

    jobUpload.publishDataJob("example", jobResource, "example-reason");

    refreshRemoteGitDirectoryWithLatestChanges();
    Assertions.assertTrue(new File(this.remoteRepositoryDir, "example").exists());

    jobUpload.deleteDataJob("example", "example-reason");
    refreshRemoteGitDirectoryWithLatestChanges();

    var commits = Iterables.toArray(remoteGit.log().call(), RevCommit.class);
    Assertions.assertEquals(2, commits.length);
    Assertions.assertEquals("user", commits[0].getAuthorIdent().getName());
    Assertions.assertFalse(new File(this.remoteRepositoryDir, "example").exists());
  }

  @Test
  public void testICanOverrideTheDefaultTempDirectoryAndUploadAndDeleteStillWork()
      throws IOException, GitAPIException {
    jobUpload =
        new JobUpload(
            createTempDir("DIFFERENT_DIRECTORY_TEST").toFile().toString(),
            gitCredentialsProvider,
            gitWrapper,
            featureFlags,
            authorizationProvider,
            jobUploadValidator,
            jobUploadFileFilter);

    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);

    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    Resource jobResource =
        new ClassPathResource("/file_test/test_job.zip", this.getClass().getClassLoader());

    jobUpload.publishDataJob("example", jobResource, "example-reason");

    refreshRemoteGitDirectoryWithLatestChanges();
    Assertions.assertTrue(new File(this.remoteRepositoryDir, "example").exists());

    jobUpload.deleteDataJob("example", "example-reason");
    refreshRemoteGitDirectoryWithLatestChanges();

    var commits = Iterables.toArray(remoteGit.log().call(), RevCommit.class);
    Assertions.assertEquals(2, commits.length);
    Assertions.assertEquals("user", commits[0].getAuthorIdent().getName());
    Assertions.assertFalse(new File(this.remoteRepositoryDir, "example").exists());
  }

  @Test
  public void testGetDataJob(@TempDir Path tempDir) throws Exception {
    Mockito.when(featureFlags.isSecurityEnabled()).thenReturn(true);
    Mockito.when(authorizationProvider.getUserId(Mockito.any())).thenReturn("user");

    Resource jobResource =
        new ClassPathResource("/file_test/test_job.zip", this.getClass().getClassLoader());
    jobUpload.publishDataJob("example", jobResource, "example-reason");
    refreshRemoteGitDirectoryWithLatestChanges();

    Optional<Resource> zippedDataJob = jobUpload.getDataJob("example");

    Assertions.assertTrue(zippedDataJob.isPresent());
    Assertions.assertTrue(zippedDataJob.get().exists());

    byte[] zippedDataJobBytes = zippedDataJob.get().getInputStream().readAllBytes();
    Assertions.assertTrue(zippedDataJobBytes.length > 0);
    // check that valid zip is expected - first 4 chars of every zip match those
    byte[] zipSignature = {0x50, 0x4b, 0x03, 0x04};
    Assertions.assertArrayEquals(zipSignature, Arrays.copyOfRange(zippedDataJobBytes, 0, 4));
  }

  private File createZipFromDir(File directory, File zipFile) throws ZipException {
    ZipFile zip = new ZipFile(zipFile);
    zip.createSplitZipFileFromFolder(directory, new ZipParameters(), false, 0);
    return zipFile;
  }

  private File createZipFromDirWithRootFolderNameInZip(File directory, File zipFile)
      throws ZipException {
    ZipFile zip = new ZipFile(zipFile);
    ZipParameters params = new ZipParameters();
    params.setRootFolderNameInZip("foo");
    zip.createSplitZipFileFromFolder(directory, params, false, 0);
    return zipFile;
  }

  private static File writeToFile(File directory, String fileName, String content)
      throws IOException {
    FileUtils.writeStringToFile(new File(directory, fileName), content, Charset.defaultCharset());
    return new File(directory, fileName);
  }

  // @NotNull
  private static File mkdir(File file, String dirName) {
    File dir = new File(file, dirName);
    dir.mkdir();
    return dir;
  }
}
