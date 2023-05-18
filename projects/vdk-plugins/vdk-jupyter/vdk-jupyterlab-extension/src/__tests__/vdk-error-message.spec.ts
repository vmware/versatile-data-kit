/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { VdkErrorMessage } from '../components/VdkErrorMessage';

describe('VdkErrorMessage', () => {
  describe('constructor', () => {
    it('should parse the message correctly', () => {
      const message =
        'ERROR : An error occurred.\nWHAT HAPPENED : Something went wrong.\nWHY IT HAPPENED : Unknown.\nCONSEQUENCES : Nothing serious.\nCOUNTERMEASURES : Try again later.';
      const vdkErrorMessage = new VdkErrorMessage(message);

      expect(vdkErrorMessage.exception_message).toEqual(
        'ERROR : An error occurred.'
      );
      expect(vdkErrorMessage.what_happened).toEqual(
        'WHAT HAPPENED : Something went wrong.'
      );
      expect(vdkErrorMessage.why_it_happened).toEqual(
        'WHY IT HAPPENED : Unknown.'
      );
      expect(vdkErrorMessage.consequences).toEqual(
        'CONSEQUENCES : Nothing serious.'
      );
      expect(vdkErrorMessage.countermeasures).toEqual(
        'COUNTERMEASURES : Try again later.'
      );
    });

    it('should set the exception_message if the message cannot be parsed', () => {
      const message = 'This is not a valid error message.';
      const vdkErrorMessage = new VdkErrorMessage(message);

      expect(vdkErrorMessage.exception_message).toEqual(message);
      expect(vdkErrorMessage.what_happened).toEqual('');
      expect(vdkErrorMessage.why_it_happened).toEqual('');
      expect(vdkErrorMessage.consequences).toEqual('');
      expect(vdkErrorMessage.countermeasures).toEqual('');
    });
  });

  describe('__parse_message', () => {
    it('should parse the message correctly', () => {
      const message =
        'ERROR : An error occurred.\nWHAT HAPPENED : Something went wrong.\nWHY IT HAPPENED : Unknown.\nCONSEQUENCES : Nothing serious.\nCOUNTERMEASURES : Try again later.';
      const vdkErrorMessage = new VdkErrorMessage('');

      vdkErrorMessage['__parse_message'](message);

      expect(vdkErrorMessage.exception_message).toEqual(
        'ERROR : An error occurred.'
      );
      expect(vdkErrorMessage.what_happened).toEqual(
        'WHAT HAPPENED : Something went wrong.'
      );
      expect(vdkErrorMessage.why_it_happened).toEqual(
        'WHY IT HAPPENED : Unknown.'
      );
      expect(vdkErrorMessage.consequences).toEqual(
        'CONSEQUENCES : Nothing serious.'
      );
      expect(vdkErrorMessage.countermeasures).toEqual(
        'COUNTERMEASURES : Try again later.'
      );
    });

    it('should set the exception_message if the message cannot be parsed', () => {
      const message = 'This is not a valid error message.';
      const vdkErrorMessage = new VdkErrorMessage('');

      vdkErrorMessage['__parse_message'](message);

      expect(vdkErrorMessage.exception_message).toEqual(message);
      expect(vdkErrorMessage.what_happened).toEqual('');
      expect(vdkErrorMessage.why_it_happened).toEqual('');
      expect(vdkErrorMessage.consequences).toEqual('');
      expect(vdkErrorMessage.countermeasures).toEqual('');
    });
  });
});
