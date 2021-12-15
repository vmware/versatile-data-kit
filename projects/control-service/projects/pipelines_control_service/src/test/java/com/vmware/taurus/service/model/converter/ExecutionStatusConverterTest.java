/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model.converter;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.vmware.taurus.service.model.ExecutionStatus;

public class ExecutionStatusConverterTest {
   private ExecutionStatusConverter converter = new ExecutionStatusConverter();

   @Test
   public void testConvertToDatabaseColumn_nullExecutionStatus_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToDatabaseColumn(null));
   }

   @Test
   public void testConvertToDatabaseColumn_executionStatusSuccess_shouldReturnSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.SUCCEEDED;
      Integer actualDbValue = converter.convertToDatabaseColumn(expectedExecutionStatus);

      Assertions.assertEquals(expectedExecutionStatus.getDbValue(), actualDbValue);
   }

   @Test
   public void testConvertToEntityAttribute_nullDbValue_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToEntityAttribute(null));
   }

   @Test
   public void testConvertToEntityAttribute_notExistingDbValue_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToEntityAttribute(-1));
   }

   @Test
   public void testConvertToEntityAttribute_dbValueTwo_shouldReturnExecutionStatusSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.SUCCEEDED;
      ExecutionStatus actualExecutionStatus =
            converter.convertToEntityAttribute(expectedExecutionStatus.getDbValue());

      Assertions.assertEquals(expectedExecutionStatus, actualExecutionStatus);
   }

   @Test
   public void testConvertToEntityAttribute_dbValueThree_shouldReturnExecutionStatusPlatformError() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.PLATFORM_ERROR;
      ExecutionStatus actualExecutionStatus = converter.convertToEntityAttribute(3);

      Assertions.assertEquals(expectedExecutionStatus, actualExecutionStatus);
   }
}
