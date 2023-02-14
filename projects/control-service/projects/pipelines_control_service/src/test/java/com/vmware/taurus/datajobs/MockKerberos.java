/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.google.common.io.Files;
import com.vmware.taurus.service.credentials.KerberosCredentialsRepository;
import lombok.SneakyThrows;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;

import java.io.File;
import java.util.HashSet;
import java.util.Optional;
import java.util.Random;
import java.util.Set;

import static org.mockito.AdditionalAnswers.answer;
import static org.mockito.AdditionalAnswers.answerVoid;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Registers a bean with a mock, but fairly functional, implementation of a {@link
 * KerberosCredentialsRepository}
 */
@Profile("MockKerberos")
@Configuration
public class MockKerberos {

  private final Set<String> principals = new HashSet<>();
  private final Random rand = new Random();

  @Bean
  @Primary
  public KerberosCredentialsRepository mockCredentialsRepository() {
    KerberosCredentialsRepository mock = mock(KerberosCredentialsRepository.class);
    doAnswer(answerVoid(this::createPrincipalMock)).when(mock).createPrincipal(any(), any());
    when(mock.principalExists(any())).thenAnswer(answer(principals::contains));
    doAnswer(answer(principals::remove)).when(mock).deletePrincipal(any());
    return mock;
  }

  private void createPrincipalMock(String principal, Optional<File> localKeyTab) {
    principals.add(principal);
    byte[] keytab = new byte[100];
    rand.nextBytes(keytab);
    localKeyTab.ifPresent(file -> writeBytes(keytab, file));
  }

  @SneakyThrows
  private void writeBytes(byte[] keytab, File file) {
    Files.write(keytab, file);
  }
}
