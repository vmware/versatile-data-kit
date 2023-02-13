/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobDeployment } from '../../model';

import { ExecutionSuccessRatePipe } from './execution-success-rate.pipe';

describe('ExecutionSuccessRatePipe', () => {
    let localeId: string;
    let pipe: ExecutionSuccessRatePipe;
    let deployments: DataJobDeployment[];

    beforeEach(() => {
        localeId = 'en-US';
        pipe = new ExecutionSuccessRatePipe(localeId);
        deployments = [
            {
                successfulExecutions: 20,
                failedExecutions: 5
            } as DataJobDeployment
        ];
    });

    it('should verify instance is created', () => {
        // Then
        expect(pipe).toBeDefined();
    });

    describe('Methods::', () => {
        describe('|transform|', () => {
            it(`should verify will return '' when no deployments or Empty Array`, () => {
                // When
                const r1 = pipe.transform(null);
                const r2 = pipe.transform(undefined);
                const r3 = pipe.transform([]);

                // Then
                expect(r1).toEqual('');
                expect(r2).toEqual('');
                expect(r3).toEqual('');
            });

            it(`should verify will return '' when sum of all all executions is 0`, () => {
                // Given
                deployments[0].successfulExecutions = 0;
                deployments[0].failedExecutions = 0;

                // When
                const r = pipe.transform(deployments);

                // Then
                expect(r).toEqual('');
            });

            it('should verify will return 100% when no failed executions', () => {
                // Given
                deployments[0].failedExecutions = 0;

                // When
                const r = pipe.transform(deployments);

                // Then
                expect(r).toEqual('100.00%');
            });

            it('should verify will return percent of success and number of failed executions (case 1)', () => {
                // When
                const r = pipe.transform(deployments);

                // Then
                expect(r).toEqual('80.00% (5 failed)');
            });

            it('should verify will return percent of success and number of failed executions (case 2)', () => {
                // Given
                deployments[0].successfulExecutions = 18;
                deployments[0].failedExecutions = 15;

                // When
                const r = pipe.transform(deployments);

                // Then
                expect(r).toEqual('54.55% (15 failed)');
            });
        });
    });
});
