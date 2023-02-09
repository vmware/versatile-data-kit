

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation */

import { Subscription } from 'rxjs';

import { CallFake } from '../../../unit-testing';

import { TaurusObject } from './taurus-object.model';

describe('TaurusObject', () => {
    it('should verify instance is created', () => {
        // When
        const instance = new TaurusObject();

        // Then
        expect(instance).toBeDefined();
        expect(instance).toBeInstanceOf(TaurusObject);
    });

    describe('Properties::', () => {
        describe('|subscriptions|', () => {
            it('should verify default value is empty Array', () => {
                // Given
                const instance = new TaurusObject();

                // Then
                expect(instance['subscriptions']).toEqual([]);
            });
        });
    });

    describe('Methods::', () => {
        describe('|dispose|', () => {
            it('should verify will clean all subscriptions', () => {
                // Given
                const subscription1 = jasmine.createSpyObj<Subscription>('subscription1', ['unsubscribe']);
                const subscription2 = jasmine.createSpyObj<Subscription>('subscription2', ['unsubscribe']);
                const subscription3 = jasmine.createSpyObj<Subscription>('subscription3', ['unsubscribe']);
                const instance = new TaurusObject();
                instance['subscriptions'].push(subscription1, null, subscription2, undefined, subscription3);

                // When
                instance.dispose();

                // Then
                expect(subscription1.unsubscribe).toHaveBeenCalled();
                expect(subscription2.unsubscribe).toHaveBeenCalled();
                expect(subscription3.unsubscribe).toHaveBeenCalled();
            });
        });

        describe('|removeSubscriptionRef|', () => {
            let subscription1: Subscription;
            let subscription2: Subscription;
            let subscription3: Subscription;
            let instance: TaurusObject;

            beforeEach(() => {
                subscription1 = new Subscription();
                subscription2 = new Subscription();
                subscription3 = new Subscription();
                instance = new TaurusObject();
            });

            it('should verify will remove provided subscription from buffer', () => {
                // Given
                instance['subscriptions'].push(subscription1, null, undefined, subscription2, subscription3);
                const unsubscribeSpy = spyOn(subscription2, 'unsubscribe').and.callThrough();

                // Then 1
                expect(instance['subscriptions'].length).toEqual(5);

                // When
                // @ts-ignore
                const value = instance.removeSubscriptionRef(subscription2);

                // Then 2
                expect(value).toBeTrue();
                expect(unsubscribeSpy).toHaveBeenCalled();
                expect(instance['subscriptions'].length).toEqual(4);
            });

            it('should verify will remove provided subscription from buffer and unsubscribe error will be logged in console', () => {
                // Given
                instance['subscriptions'].push(subscription1);
                const error = new Error('Error');
                const unsubscribeSpy = spyOn(subscription1, 'unsubscribe').and.throwError(error);
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // When
                // @ts-ignore
                const value = instance.removeSubscriptionRef(subscription1);

                // Then 2
                expect(value).toBeFalse();
                expect(unsubscribeSpy).toHaveBeenCalled();
                expect(consoleErrorSpy).toHaveBeenCalledWith(`Taurus Object failed to unsubscribe from rxjs stream!`, error);
            });

            it(`should verify will unsubscribe even reference doesn't exist in buffer`, () => {
                // Given
                instance['subscriptions'].push(subscription2, null, undefined);
                const unsubscribeSpy = spyOn(subscription1, 'unsubscribe').and.callThrough();

                // Then 1
                expect(instance['subscriptions'].length).toEqual(3);

                // When
                // @ts-ignore
                const value = instance.removeSubscriptionRef(subscription1);

                // Then 2
                expect(value).toBeTrue();
                expect(unsubscribeSpy).toHaveBeenCalled();
                expect(instance['subscriptions'].length).toEqual(3);
            });

            it(`should verify will return false when provided reference is not Subscription instance`, () => {
                // Given
                instance['subscriptions'].push(subscription1, subscription2);

                // Then 1
                expect(instance['subscriptions'].length).toEqual(2);

                // When
                // @ts-ignore
                const value1 = instance.removeSubscriptionRef(null);
                // @ts-ignore
                const value2 = instance.removeSubscriptionRef(undefined);

                // Then 2
                expect(value1).toBeFalse();
                expect(value2).toBeFalse();
                expect(instance['subscriptions'].length).toEqual(2);
            });
        });

        describe('|ngOnDestroy|', () => {
            it('should verify will invoke correct method', () => {
                // Given
                const instance = new TaurusObject();
                const disposeSpy = spyOn(instance, 'dispose').and.callFake(CallFake);

                // When
                instance.ngOnDestroy();

                // Then
                expect(disposeSpy).toHaveBeenCalled();
            });
        });
    });
});
