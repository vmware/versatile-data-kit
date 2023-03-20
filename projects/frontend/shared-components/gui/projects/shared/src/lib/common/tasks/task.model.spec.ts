/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../utils';

import { createTaskIdentifier, extractTaskFromIdentifier } from './task.model';

describe('Tasks', () => {
    describe('|createTaskIdentifier|', () => {
        it('should verify will return expected value', () => {
            // Given
            const task = 'create_entity';
            const dateNowISO = new Date().toISOString();
            const taskIdentifier = `${task} __ ${dateNowISO}`;
            const dateISOSpy = spyOn(CollectionsUtil, 'dateISO').and.returnValue(dateNowISO);
            const interpolateStringSpy = spyOn(CollectionsUtil, 'interpolateString' as never).and.returnValue(taskIdentifier as never);
            const expected = `${task} __ ${dateNowISO}`;

            // When
            const response = createTaskIdentifier(task);

            // Then
            expect(response).toEqual(expected);
            expect(dateISOSpy).toHaveBeenCalled();
            // @ts-ignore
            expect(interpolateStringSpy).toHaveBeenCalledWith('%s __ %s' as never, task as never, dateNowISO as never);
        });

        it('should verify will return value undefined when no task provided', () => {
            // When
            const response = createTaskIdentifier(null);

            // Then
            expect(response).toBeUndefined();
        });
    });

    describe('|extractTaskFromIdentifier|', () => {
        it('should verify will return Task from provided identifier', () => {
            // Given
            const dateNowISO = new Date().toISOString();
            const taskIdentifier = `delete_entity __ ${dateNowISO}`;
            const expected = 'delete_entity';

            // When
            const response = extractTaskFromIdentifier(taskIdentifier);

            // Then
            expect(response).toEqual(expected);
        });
    });
});
