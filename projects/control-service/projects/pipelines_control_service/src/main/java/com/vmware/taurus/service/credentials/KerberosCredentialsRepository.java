/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.credentials;

import com.vmware.taurus.ServiceAppPropNames;
import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.ExternalSystemError.MainExternalSystem;
import lombok.SneakyThrows;
import org.apache.commons.lang3.Validate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;
import org.zeroturnaround.exec.ProcessExecutor;
import org.zeroturnaround.exec.ProcessResult;
import org.zeroturnaround.exec.stream.slf4j.Slf4jStream;

import java.io.File;
import java.util.Optional;

/**
 * CRUD operations on principals and keytab files.
 *
 * <p>It requires to have kadmin installed locally and in PATH and /bin/sh .
 *
 * <p>NOTE: KerberosCredentialsServiceTestManual is currently manual test, use it when making
 * changes to test.
 */
@Profile("!MockKerberos")
@Component
@ConditionalOnProperty(
    value = ServiceAppPropNames.CREDENTIALS_REPOSITORY_TYPE,
    havingValue = "KERBEROS",
    matchIfMissing = false)
public class KerberosCredentialsRepository implements CredentialsRepository {
  private static final Logger log = LoggerFactory.getLogger(KerberosCredentialsRepository.class);

  private final String kadminUser;
  private final String kadminPassword;

  public KerberosCredentialsRepository(
      @Value("${datajobs.kadmin_user}") String kadminUser,
      @Value("${datajobs.kadmin_password}") String kadminPassword) {
    this.kadminUser = kadminUser;
    this.kadminPassword = kadminPassword;
    log.info("Credentials repository used will be Kerberos");
    checkDependencies();
  }

  private void checkDependencies() {
    try {
      ProcessExecutor executor = new ProcessExecutor();
      executor.readOutput(true);
      ProcessResult result = executor.command("/bin/sh", "-c", "which kadmin").execute();
      if (result == null || result.getExitValue() != 0) {
        log.error(
            "Missing required dependencies. "
                + " kadmin are missing or are not found on PATH."
                + "Possible reason: "
                + (result != null ? result.getOutput().getUTF8() : "")
                + "Without those credential management will not work. ");
      }
      var krbConf = System.getenv().getOrDefault("KRB5_CONFIG", "/etc/krb5.conf");
      if (!new File(krbConf).isFile()) {
        log.error(
            "Missing required dependencies. "
                + "{} is missing. "
                + "Without this credential management cannot work. ",
            krbConf);
      }
    } catch (Exception e) {
      log.error(
          "Checking dependencies failed."
              + "See exception for more information and root cause. "
              + "It's possible that credentials management will not be working properly or at all.",
          e);
    }
  }

  /**
   * Create a new Principal and keytab for the given principal. If the principal already existed,
   * the keytab will be refreshed and previous keytab file cannot be used anymore.
   *
   * @param principal Kerberos principal is a unique identity in Kerberos (KDC).
   * @param keytabLocation where to export the keytab file for the new principal. If there's already
   *     existing file, it will be deleted/overwritten. If variable is not present keytab will not
   *     be generated. see also https://web.mit.edu/kerberos/krb5-devel/doc/basic/keytab_def.html
   */
  @Override
  public void createPrincipal(String principal, Optional<File> keytabLocation) {
    Validate.notBlank(principal, "principal must not be blank");
    if (!principalExists(principal)) {
      createPrincipal(principal);
    }
    if (keytabLocation.isPresent()) {
      exportKeytab(principal, keytabLocation.get());
    }
  }

  private void createPrincipal(String principal) {
    var success = execute_kadmin_command("add_principal -randkey " + principal, "created");
    if (!success) {
      String msg =
          String.format(
              "Failed to execute add principal %s. "
                  + "It return error code. Check logs for more details",
              principal);
      log.error(msg);
      throw new ExternalSystemError(MainExternalSystem.KERBEROS, msg);
    }
    log.debug("Created {} successfully", principal);
  }

  private void exportKeytab(String principal, File keytabLocation) {
    boolean success;
    keytabLocation.delete();
    success =
        execute_kadmin_command(
            String.format("ktadd -k %s %s", keytabLocation.getAbsolutePath(), principal),
            "Entry for principal");
    if (!success) {
      String msg =
          String.format(
              "Failed to create principal keytab for principal %s. "
                  + "It return error code. Check logs for more details",
              principal);
      log.error(msg);
      throw new ExternalSystemError(MainExternalSystem.KERBEROS, msg);
    }
  }

  /**
   * Check if principal exists in KDC.
   *
   * @param principal Kerberos principal is a unique identity in Kerberos (KDC).
   */
  @Override
  public boolean principalExists(String principal) {
    Validate.notBlank(principal, "principal must not be blank");
    return execute_kadmin_command("get_principal " + principal, "Expiration date");
  }

  /**
   * Delete principal. It will also invalidate any keytab created for this principal. If job is
   * already deleted, this is no op.
   *
   * @param principal Kerberos principal is a unique identity in Kerberos (KDC).
   */
  @Override
  @SneakyThrows
  public void deletePrincipal(String principal) {
    Validate.notBlank(principal, "principal must not be blank");
    if (principalExists(principal)) {
      var success = execute_kadmin_command("delete_principal -force " + principal, "deleted");
      if (!success) {
        String msg =
            String.format(
                "Failed to delete principal %s. "
                    + "It return error code. Check logs for more details",
                principal);
        log.error(msg);
        throw new ExternalSystemError(MainExternalSystem.KERBEROS, msg);
      }
    }
  }

  /**
   * Execute (kerberos) kadmin command
   *
   * @param cmd the kadmin command e.g ktadd, add_principal
   * @param expectedInOutput kadmin commands always return 0 so exit code cannot be used as usual,
   *     so we trick it by checking if substring is found in output. TODO: That's brittle so we will
   *     probably have some maintenance cost for this. In the future we should try some libraries.
   *     Few that were tried and did not work are apache directory-kerby (hit issue DIRKRB-534) and
   *     pt.tecnico.dsi:kadmin (was hard to use)
   * @return true if command is successful otherwise false.
   */
  @SneakyThrows
  private boolean execute_kadmin_command(String cmd, String expectedInOutput) {
    String full_command =
        String.format("kadmin -w '%s' -p %s -q '%s'", kadminPassword, kadminUser, cmd);
    log.debug("Execute kadmin command: {}", cmd);
    ProcessExecutor processExecutor =
        new ProcessExecutor()
            .command("/bin/sh", "-c", full_command)
            .redirectOutputAlsoTo(Slf4jStream.of(log).asInfo())
            .redirectErrorAlsoTo(Slf4jStream.of(log).asInfo())
            .readOutput(true);

    ProcessResult result = processExecutor.start().getFuture().get();
    if (result.getExitValue() == 0) {
      if (!expectedInOutput.isBlank()) {
        String stdout = result.getOutput().getUTF8();
        return stdout.contains(expectedInOutput);
      }
    }
    return false;
  }
}
