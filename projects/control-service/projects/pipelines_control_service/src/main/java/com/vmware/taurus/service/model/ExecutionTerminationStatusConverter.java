/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import javax.persistence.AttributeConverter;
import javax.persistence.Converter;
import java.util.Arrays;

import com.google.common.primitives.Ints;

@Converter
public class ExecutionTerminationStatusConverter implements AttributeConverter<ExecutionTerminationStatus, String> {

   @Override
   public String convertToDatabaseColumn(ExecutionTerminationStatus terminationStatus) {
      return terminationStatus != null ? String.valueOf(terminationStatus.getInteger()) : null;
   }

   @Override
   public ExecutionTerminationStatus convertToEntityAttribute(String dbValueString) {
      if (dbValueString == null) {
         return null;
      }

      Integer dbValueInteger = Ints.tryParse(dbValueString);
      return Arrays.stream(ExecutionTerminationStatus.values())
            .filter(terminationStatus -> terminationStatus.getInteger().equals(dbValueInteger))
            .findAny()
            .orElse(null);
   }
}
