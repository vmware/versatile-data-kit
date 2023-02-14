/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.upload;

import net.lingala.zip4j.ZipFile;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Class responsible to handle file operations of primarily for {@link JobUpload} but is generic
 * enough to be used in more broad context.
 *
 * <p>TODO: deprecate this class and reuse the FileUtils class from Apache
 */
public class FileUtils {

  /**
   * Helper class that will delete the file upon close. Used to return resource hold in temp file
   * which after it's sent can be deleted.
   */
  static class CleanupFileInputStreamResource extends FileSystemResource {
    public CleanupFileInputStreamResource(File file) {
      super(file);
    }

    @Override
    public InputStream getInputStream() throws IOException {
      return new DeleteOnCloseFileInputStream(super.getFile());
    }

    private static final class DeleteOnCloseFileInputStream extends FileInputStream {

      private File file;

      DeleteOnCloseFileInputStream(File file) throws FileNotFoundException {
        super(file);
        this.file = file;
      }

      @Override
      public void close() throws IOException {
        super.close();
        file.delete();
      }
    }
  }

  public static Path createTempDir(String prefix) throws IOException {
    return Files.createTempDirectory(prefix);
  }

  public static void removeDir(Path tempDirPath) throws IOException {
    if (Files.exists(tempDirPath)) {
      Files.walk(tempDirPath)
          .sorted(Comparator.reverseOrder())
          .map(Path::toFile)
          .forEach(File::delete);
    }
  }

  public static void copy(String jobFolder, String jobRepoFolder, String jobName)
      throws IOException {
    String jobNewLocation = jobRepoFolder + File.separator + jobName;
    if (Files.exists(Paths.get(jobNewLocation))) {
      removeDir(Paths.get(jobNewLocation));
    }
    Files.move(Paths.get(jobFolder), Paths.get(jobNewLocation));
  }

  /**
   * The method unzips zip file received as binary in this format: - job.zip - job_folder - x.py -
   * y.sql
   *
   * <p>in case the job_folder name is different than the job name the method will rename it to be
   * the same as the job name.
   *
   * <p>The function has a protection against zip slip exploit but it doesn't have against zip bomb
   * (which is type of DOS attack). If someone tries to upload zipbomb then the pod may restart so
   * it's not that big of an issue.
   *
   * @param resource binary containing the zip file sent to the service
   * @param tempDir temporary directory containing all the files for the upload process
   * @param jobName name of the data job so we can unzip the job contents in folder with that name
   * @return folder containing data job files
   * @throws IOException
   */
  public static File unzipDataJob(Resource resource, File tempDir, String jobName)
      throws IOException {
    File jobZipFile = new File(tempDir, "job_zip.zip");
    File jobTempDir = new File(tempDir, "job_dir");
    org.apache.commons.io.FileUtils.copyInputStreamToFile(resource.getInputStream(), jobZipFile);
    try (ZipFile theZipFile = new ZipFile(jobZipFile)) {
      theZipFile.extractAll(jobTempDir.getAbsolutePath());
    }
    List<Path> paths = Files.list(jobTempDir.toPath()).collect(Collectors.toList());
    return paths.get(0).toFile();
  }

  public static void zipDataJob(File fromDataJobDirectory, File intoNewZipFile) throws IOException {
    try (ZipFile theZipFile = new ZipFile(intoNewZipFile)) {
      theZipFile.addFolder(fromDataJobDirectory);
    }
  }

  public static File renameFile(String oldPath, String newPath) throws IOException {
    File newFile = Paths.get(newPath).toFile();
    File oldFile = Paths.get(oldPath).toFile();
    boolean renamed = oldFile.renameTo(newFile);
    if (!renamed) {
      throw new IOException(String.format("Unable to rename file: %s to %s", oldFile, newFile));
    }
    return newFile;
  }
}
