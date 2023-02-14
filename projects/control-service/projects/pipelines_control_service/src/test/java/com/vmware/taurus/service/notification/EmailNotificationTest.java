/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.notification;

import javax.mail.Address;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import com.vmware.taurus.ControlplaneApplication;

@SpringBootTest(classes = ControlplaneApplication.class)
public class EmailNotificationTest {

  @Autowired private EmailNotification emailNotification;

  @Test
  public void testConcatAddresses_nullAddresses_shouldReturnNull() {
    String result = emailNotification.concatAddresses(null);
    Assertions.assertNull(result);
  }

  @Test
  public void testConcatAddresses_validAddresses_shouldReturnNull() {
    String address1 = "a@a.a";
    String address2 = "b@b.b";
    String result =
        emailNotification.concatAddresses(
            new Address[] {createAddress(address1), createAddress(address2)});

    Assertions.assertEquals(address1 + " " + address2, result);
  }

  private static Address createAddress(String address) {
    return new Address() {
      @Override
      public String getType() {
        return null;
      }

      @Override
      public String toString() {
        return address;
      }

      @Override
      public boolean equals(Object address) {
        return false;
      }
    };
  }
}
