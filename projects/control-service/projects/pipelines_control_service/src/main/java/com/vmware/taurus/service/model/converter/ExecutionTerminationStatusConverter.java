/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model.converter;

import javax.persistence.AttributeConverter;
import javax.persistence.Converter;
import java.util.Arrays;

import com.google.common.primitives.Ints;

import com.vmware.taurus.service.model.ExecutionStatus;

@Converter
public class ExecutionTerminationStatusConverter implements AttributeConverter<ExecutionStatus, String> {

   @Override
   public String convertToDatabaseColumn(ExecutionStatus executionStatus) {
      return executionStatus != null ? String.valueOf(executionStatus.getAlertValue()) : null;
   }

   @Override
   public ExecutionStatus convertToEntityAttribute(String dbValueString) {
      if (dbValueString == null) {
         return null;
      }

      Integer dbValueInteger = Ints.tryParse(dbValueString);
      return Arrays.stream(ExecutionStatus.values())
            .filter(terminationStatus -> terminationStatus.getAlertValue().equals(dbValueInteger))
            .findAny()
            .orElse(null);
   }
}
