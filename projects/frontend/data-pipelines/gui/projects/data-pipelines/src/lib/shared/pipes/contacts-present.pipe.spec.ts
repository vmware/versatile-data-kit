/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobContacts } from '../../model';

import { ContactsPresentPipe } from './contacts-present.pipe';

describe('ContactsPresentPipe', () => {
    it('should verify instance is created', () => {
        // When
        const instance = new ContactsPresentPipe();

        // Then
        expect(instance).toBeDefined();
    });

    describe('Methods::', () => {
        let pipe: ContactsPresentPipe;

        beforeEach(() => {
            pipe = new ContactsPresentPipe();
        });

        describe('|transform|', () => {
            const parameters: Array<{ contacts: DataJobContacts; expected: boolean }> = [
                { contacts: null, expected: false },
                {
                    contacts: {
                        notifiedOnJobSuccess: undefined,
                        notifiedOnJobDeploy: undefined,
                        notifiedOnJobFailurePlatformError: undefined,
                        notifiedOnJobFailureUserError: undefined
                    },
                    expected: false
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: [],
                        notifiedOnJobDeploy: [],
                        notifiedOnJobFailurePlatformError: [],
                        notifiedOnJobFailureUserError: []
                    },
                    expected: false
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: ['alpha@abc.com'],
                        notifiedOnJobDeploy: [],
                        notifiedOnJobFailurePlatformError: [],
                        notifiedOnJobFailureUserError: []
                    },
                    expected: true
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: [],
                        notifiedOnJobDeploy: ['beta@abc.com'],
                        notifiedOnJobFailurePlatformError: [],
                        notifiedOnJobFailureUserError: []
                    },
                    expected: true
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: [],
                        notifiedOnJobDeploy: [],
                        notifiedOnJobFailurePlatformError: ['gama@abc.com'],
                        notifiedOnJobFailureUserError: []
                    },
                    expected: true
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: [],
                        notifiedOnJobDeploy: [],
                        notifiedOnJobFailurePlatformError: [],
                        notifiedOnJobFailureUserError: ['delta@abc.com']
                    },
                    expected: true
                },
                {
                    contacts: {
                        notifiedOnJobSuccess: ['alpha@abc.com'],
                        notifiedOnJobDeploy: ['beta@abc.com'],
                        notifiedOnJobFailurePlatformError: ['gama@abc.com'],
                        notifiedOnJobFailureUserError: ['delta@abc.com']
                    },
                    expected: true
                }
            ];

            let cnt = 0;
            for (const params of parameters) {
                cnt++;

                it(`should verify will return ${ (params.expected as unknown) as string } case ${ cnt }`, () => {
                    // When
                    const value = pipe.transform(params.contacts);

                    // Then
                    expect(value).toEqual(params.expected);
                });
            }
        });
    });
});
