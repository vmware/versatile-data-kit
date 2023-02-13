/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'extractContacts'
})
export class ExtractContactsPipe implements PipeTransform {

    static transform(contacts: string[]): string[] {
        if (Array.isArray(contacts) && contacts.length) {
            return contacts;
        } else {
            return [];
        }
    }

    transform(contacts: string[]): string[] {
        return ExtractContactsPipe.transform(contacts);
    }

}
