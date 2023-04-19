/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Class that represents VDK Error messages in the UI
 * Check projects/vdk-core/src/vdk/internal/core/errors.py too see more about VDK errors
 */
export class VdkErrorMessage {
  public exception_message: String;
  public what_happened: String;
  public why_it_happened: String;
  public consequences: String;
  public countermeasures: String;

  constructor(message: String) {
    this.exception_message = '';
    this.what_happened = '';
    this.why_it_happened = '';
    this.consequences = '';
    this.countermeasures = '';

    this.__parse_message(message);
  }

  private __parse_message(message: String): void {
    const keys: (keyof VdkErrorMessage)[] = [
      'exception_message',
      'what_happened',
      'why_it_happened',
      'consequences',
      'countermeasures'
    ];
    const delimiters = [
      'ERROR : ',
      'WHAT HAPPENED :',
      'WHY IT HAPPENED :',
      'CONSEQUENCES :',
      'COUNTERMEASURES :'
    ];
    const lines = message.split('\n');
    let keyIndex = 0;
    for (let i = 0; i < lines.length; i++) {
      const delimiterIndex = lines[i].indexOf(delimiters[keyIndex]);
      if (delimiterIndex !== -1) {
        this[keys[keyIndex]] =
          delimiters[keyIndex] +
          lines[i].substring(delimiterIndex + delimiters[keyIndex].length);
        keyIndex++;
        if (keyIndex === keys.length) {
          break;
        }
      } else {
        this.exception_message = message;
      }
    }
  }
}
