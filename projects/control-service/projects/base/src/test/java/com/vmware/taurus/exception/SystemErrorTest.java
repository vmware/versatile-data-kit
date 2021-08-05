package com.vmware.taurus.exception;

import org.junit.Test;
import org.springframework.http.HttpStatus;

import static org.junit.Assert.assertThrows;

public class SystemErrorTest {

   private static class InvalidSystemError extends SystemError implements UserFacingError {

      InvalidSystemError() {
         super("bla", "bla", "bla", "bla", null);
      }

      @Override
      public HttpStatus getHttpStatus() {
         return HttpStatus.OK;
      }
   }
   @Test
   public void testValidation() {
      assertThrows(Bug.class, InvalidSystemError::new);
   }
}