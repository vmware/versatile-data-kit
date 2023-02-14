/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import net.lingala.zip4j.ZipFile;
import net.lingala.zip4j.exception.ZipException;
import net.lingala.zip4j.model.ZipParameters;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;

public class FileUtilsTest {

  static class JobZipBuilder implements AutoCloseable {

    private final ZipFile zipFile;

    JobZipBuilder(Path zipFilePath) {
      this.zipFile = new ZipFile(zipFilePath.toFile());
    }

    public void addFile(String fileNameInZip, int uncompressedSizeInKB) throws ZipException {
      var parameters = new ZipParameters();
      parameters.setFileNameInZip(fileNameInZip);

      this.zipFile.addStream(
          new ByteArrayInputStream(
              "0".repeat(uncompressedSizeInKB * 1024).getBytes(StandardCharsets.UTF_8)),
          parameters);
    }

    @Override
    public void close() throws Exception {
      this.zipFile.close();
    }
  }

  @Test
  public void endToEndFileTest() throws IOException, URISyntaxException {
    Resource zipResource = new ClassPathResource("file_test/test_job.zip");
    Path tempDirPathFirst = FileUtils.createTempDir("test1_");
    Path tempDirPathSecond = FileUtils.createTempDir("test2_");

    File unzippedFile = FileUtils.unzipDataJob(zipResource, tempDirPathFirst.toFile(), "example");
    Assertions.assertTrue(unzippedFile.exists());

    FileUtils.copy(unzippedFile.toString(), tempDirPathSecond.toString(), "example");
    File newTestFileLocation = new File(tempDirPathSecond.toFile(), "example");
    Assertions.assertTrue(newTestFileLocation.exists());
    Assertions.assertTrue(newTestFileLocation.isDirectory());
    Assertions.assertTrue(newTestFileLocation.list().length > 0);

    File secondUnzippedFile =
        FileUtils.unzipDataJob(zipResource, tempDirPathFirst.toFile(), "example");
    Assertions.assertTrue(secondUnzippedFile.exists());
    Assertions.assertTrue(secondUnzippedFile.isDirectory());
    Assertions.assertTrue(secondUnzippedFile.list().length > 0);

    FileUtils.copy(secondUnzippedFile.toString(), tempDirPathSecond.toString(), "example");
    Assertions.assertTrue(newTestFileLocation.exists());

    File renamedTestFile = new File(tempDirPathSecond.toFile(), "new_example");
    Assertions.assertThrows(
        IOException.class,
        () ->
            FileUtils.renameFile(
                unzippedFile.getAbsolutePath(), renamedTestFile.getAbsolutePath()));

    FileUtils.renameFile(newTestFileLocation.getAbsolutePath(), renamedTestFile.getAbsolutePath());
    Assertions.assertTrue(renamedTestFile.exists());

    FileUtils.removeDir(tempDirPathFirst);
    Assertions.assertTrue(!tempDirPathFirst.toFile().exists());

    FileUtils.removeDir(tempDirPathSecond);
    Assertions.assertTrue(!tempDirPathSecond.toFile().exists());
  }

  @Test
  public void testZipDirectory(@TempDir Path tempDir) throws IOException {
    Path directory = Paths.get(tempDir.toString(), "test-directory");
    Path zipFile = Paths.get(tempDir.toString(), "zip-file");

    Files.createDirectory(directory);
    Files.writeString(Paths.get(directory.toString(), "config.ini"), "team=xxx");
    Path subDir = Paths.get(directory.toString(), "subdir");
    Files.createDirectory(subDir);
    Files.writeString(Paths.get(subDir.toString(), "x.py"), "import this");

    FileUtils.zipDataJob(directory.toFile(), zipFile.toFile());

    byte[] zipFileBytes = Files.readAllBytes(zipFile);
    System.out.println(zipFileBytes.length);
    Assertions.assertTrue(zipFileBytes.length > 0);
    // check that valid zip is expected - first 4 chars of every zip match those
    byte[] zipSignature = {0x50, 0x4b, 0x03, 0x04};
    Assertions.assertArrayEquals(zipSignature, Arrays.copyOfRange(zipFileBytes, 0, 4));

    File unzipped =
        FileUtils.unzipDataJob(new FileSystemResource(zipFile.toFile()), tempDir.toFile(), "name");
    Assertions.assertTrue(unzipped.isDirectory());
    Assertions.assertTrue(new File(unzipped, "config.ini").isFile());
    Assertions.assertTrue(new File(unzipped, "subdir").isDirectory());
    Assertions.assertTrue(new File(new File(unzipped, "subdir"), "x.py").isFile());
  }

  @Test
  public void testUnZip_zipSlipExploit(@TempDir Path tempDir) throws Exception {
    Path zipFile = Paths.get(tempDir.toString(), "zip-file.zip");
    JobZipBuilder builder = new JobZipBuilder(zipFile);
    builder.addFile("job/../../../forbidden", 10);
    builder.addFile("../../../forbidden", 10);
    builder.close();

    Assertions.assertThrows(
        ZipException.class,
        () ->
            FileUtils.unzipDataJob(
                new FileSystemResource(zipFile.toFile()), tempDir.toFile(), "name"));
  }
}
