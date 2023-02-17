/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

import { CollectionsUtil } from '@vdk/shared';

import { DataJobContacts } from '../../model';

@Pipe({
    name: 'contactsPresent'
})
export class ContactsPresentPipe implements PipeTransform {
    /**
     * @inheritDoc
     */
    transform(contacts: DataJobContacts): boolean {
        return CollectionsUtil.isDefined(contacts) &&
            (
                ContactsPresentPipe.contactIsPresent(contacts.notifiedOnJobSuccess) ||
                ContactsPresentPipe.contactIsPresent(contacts.notifiedOnJobDeploy) ||
                ContactsPresentPipe.contactIsPresent(contacts.notifiedOnJobFailureUserError) ||
                ContactsPresentPipe.contactIsPresent(contacts.notifiedOnJobFailurePlatformError)
            );
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering
    private static contactIsPresent(contacts: string[]): boolean {
        return CollectionsUtil.isArray(contacts) && contacts.length > 0;
    }
}
