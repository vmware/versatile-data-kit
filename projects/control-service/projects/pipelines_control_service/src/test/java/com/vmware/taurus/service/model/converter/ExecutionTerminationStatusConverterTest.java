/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model.converter;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.converter.ExecutionTerminationStatusConverter;

public class ExecutionTerminationStatusConverterTest {
   private ExecutionTerminationStatusConverter converter = new ExecutionTerminationStatusConverter();

   @Test
   public void testConvertToDatabaseColumn_nullTerminationStatus_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToDatabaseColumn(null));
   }

   @Test
   public void testConvertToDatabaseColumn_terminationStatusSuccess_shouldReturnSuccess() {
      ExecutionStatus expectedTerminationStatus = ExecutionStatus.SUCCEEDED;
      String actualDbValue = converter.convertToDatabaseColumn(expectedTerminationStatus);

      Assertions.assertEquals(String.valueOf(expectedTerminationStatus.getAlertValue()), actualDbValue);
   }

   @Test
   public void testConvertToEntityAttribute_nullDbValue_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToEntityAttribute(null));
   }

   @Test
   public void testConvertToEntityAttribute_dbValueText_shouldReturnNullValue() {
      Assertions.assertNull(converter.convertToEntityAttribute("test_db_value"));
   }

   @Test
   public void testConvertToEntityAttribute_dbValueSuccess_shouldReturnTerminationStatusSuccess() {
      ExecutionStatus expectedTerminationStatus = ExecutionStatus.SUCCEEDED;
      ExecutionStatus actualTerminationStatus =
            converter.convertToEntityAttribute(String.valueOf(expectedTerminationStatus.getAlertValue()));

      Assertions.assertEquals(expectedTerminationStatus, actualTerminationStatus);
   }
}
