/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { createRouteSnapshot } from '../../../unit-testing';

import { RouteSegments, RouteState } from '../model';

import { RouteStateFactory } from './route-state.factory';

describe('RouteStateFactory', () => {
    it('should verify instance is created', () => {
        // When
        const instance = new RouteStateFactory();

        // Then
        expect(instance).toBeDefined();
    });

    describe('Methods::', () => {
        describe('|create|', () => {
            it('should verify will return RouteState from provided ActivatedRouteSnapshot', () => {
                // Given
                const routeSnapshot = createRouteSnapshot({});
                const factory = new RouteStateFactory();
                const assertion = RouteState.of(
                    new RouteSegments(
                        'entity/23',
                        { paramKey: 'prime' },
                        { entityId: 23 },
                        { search: 'test-team' },
                        new RouteSegments('domain/context', {}, {}, {}, undefined, 'domain/context'),
                        'entity/23'
                    ),
                    'domain/context/entity/23'
                );

                // When
                const routeState = factory.create(routeSnapshot, 'domain/context/entity/23');

                // Then
                expect(routeState).toEqual(assertion);
            });
        });
    });
});
