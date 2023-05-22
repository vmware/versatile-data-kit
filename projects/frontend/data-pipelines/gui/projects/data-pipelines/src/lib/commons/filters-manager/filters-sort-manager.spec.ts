/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { fakeAsync, tick } from '@angular/core/testing';

import { CallFake, URLStateManager } from '@versatiledatakit/shared';

import { FILTER_KEY, FiltersSortManager, KeyValueTuple, SORT_KEY } from './filters-sort-manager';

const FILTER_CRITERIA_F1 = 'c1';
const FILTER_CRITERIA_F2 = 'c2';
const FILTER_CRITERIA_F3 = 'c3';
const FILTER_CRITERIA_F4 = 'c4';
const FILTER_CRITERIA_F5 = 'c5';
type FILTER_CRITERIA_UNION =
    | typeof FILTER_CRITERIA_F1
    | typeof FILTER_CRITERIA_F2
    | typeof FILTER_CRITERIA_F3
    | typeof FILTER_CRITERIA_F4
    | typeof FILTER_CRITERIA_F5;

const SORT_CRITERIA_S1 = 'c1';
const SORT_CRITERIA_S2 = 'c2';
const SORT_CRITERIA_S3 = 'c3';
const SORT_CRITERIA_S4 = 'c4';
type SORT_CRITERIA_UNION = typeof SORT_CRITERIA_S1 | typeof SORT_CRITERIA_S2 | typeof SORT_CRITERIA_S3 | typeof SORT_CRITERIA_S4;

const KNOWN_FILTER_CRITERIA: FILTER_CRITERIA_UNION[] = [
    FILTER_CRITERIA_F1,
    FILTER_CRITERIA_F2,
    FILTER_CRITERIA_F3,
    FILTER_CRITERIA_F4,
    FILTER_CRITERIA_F5
];

const KNOWN_SORT_CRITERIA: SORT_CRITERIA_UNION[] = [SORT_CRITERIA_S1, SORT_CRITERIA_S2, SORT_CRITERIA_S3, SORT_CRITERIA_S4];

class MutationObserver {
    observer(_changes: Array<KeyValueTuple<FILTER_CRITERIA_UNION | SORT_CRITERIA_UNION, string>>): void {
        // No-op.
    }
}

describe('FiltersSortManager', () => {
    let urlStateManagerStub: jasmine.SpyObj<URLStateManager>;

    beforeEach(() => {
        urlStateManagerStub = jasmine.createSpyObj<URLStateManager>('urlStateManagerStub', [
            'changeBaseUrl',
            'locationToURL',
            'replaceToUrl',
            'navigateToUrl',
            'setQueryParam'
        ]);
    });

    it('should verify instance is created', () => {
        // When
        const instance = new FiltersSortManager<FILTER_CRITERIA_UNION, string, SORT_CRITERIA_UNION, string>(
            urlStateManagerStub,
            KNOWN_FILTER_CRITERIA,
            KNOWN_SORT_CRITERIA
        );

        // Then
        expect(instance).toBeDefined();
    });

    describe('Properties::', () => {
        let manager: FiltersSortManager<FILTER_CRITERIA_UNION, string, SORT_CRITERIA_UNION, string>;

        beforeEach(() => {
            manager = new FiltersSortManager(urlStateManagerStub, KNOWN_FILTER_CRITERIA, KNOWN_SORT_CRITERIA);
        });

        describe('|filterCriteria|', () => {
            it('should verify default value is empty object', () => {
                // Then
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);
            });
        });

        describe('|sortCriteria|', () => {
            it('should verify default value is empty object', () => {
                // Then
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);
            });
        });
    });

    describe('Methods::', () => {
        let manager: FiltersSortManager<FILTER_CRITERIA_UNION, string, SORT_CRITERIA_UNION, string>;

        beforeEach(() => {
            manager = new FiltersSortManager(urlStateManagerStub, KNOWN_FILTER_CRITERIA, KNOWN_SORT_CRITERIA);
        });

        describe('|hasFilter|', () => {
            it('should verify will return false when there is not such filter criteria', () => {
                // Given
                manager.filterCriteria[FILTER_CRITERIA_F1] = 'f1v';
                manager.filterCriteria[FILTER_CRITERIA_F2] = 'f2v';

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: 'f1v',
                    [FILTER_CRITERIA_F2]: 'f2v'
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasFilter(FILTER_CRITERIA_F1)).toBeTrue();
                expect(manager.hasFilter(FILTER_CRITERIA_F2)).toBeTrue();
                expect(manager.hasFilter(FILTER_CRITERIA_F3)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F4)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F5)).toBeFalse();
            });

            it(`should verify will return false when there is such filter criteria but it's value is Nil`, () => {
                // Given
                manager.filterCriteria[FILTER_CRITERIA_F1] = 'f1v';
                manager.filterCriteria[FILTER_CRITERIA_F3] = null;
                manager.filterCriteria[FILTER_CRITERIA_F5] = undefined;

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: 'f1v',
                    [FILTER_CRITERIA_F3]: null,
                    [FILTER_CRITERIA_F5]: undefined
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasFilter(FILTER_CRITERIA_F1)).toBeTrue();
                expect(manager.hasFilter(FILTER_CRITERIA_F2)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F3)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F4)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F5)).toBeFalse();
            });

            it(`should verify will return true when there is such filter criteria and it's value is not Nil`, () => {
                // Given
                manager.filterCriteria[FILTER_CRITERIA_F2] = 'f2v';
                manager.filterCriteria[FILTER_CRITERIA_F3] = 'f3v';

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F2]: 'f2v',
                    [FILTER_CRITERIA_F3]: 'f3v'
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasFilter(FILTER_CRITERIA_F1)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F2)).toBeTrue();
                expect(manager.hasFilter(FILTER_CRITERIA_F3)).toBeTrue();
                expect(manager.hasFilter(FILTER_CRITERIA_F4)).toBeFalse();
                expect(manager.hasFilter(FILTER_CRITERIA_F5)).toBeFalse();
            });
        });

        describe('|hasAnyFilter|', () => {
            it('should verify will return false when there is no filter criteria set', () => {
                // Then 1
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                // Then 2
                expect(manager.hasAnyFilter()).toBeFalse();
            });

            it(`should verify will return false when there are two filter criteria but their value is Nil`, () => {
                // Given
                manager.filterCriteria[FILTER_CRITERIA_F2] = null;
                manager.filterCriteria[FILTER_CRITERIA_F4] = undefined;

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F2]: null,
                    [FILTER_CRITERIA_F4]: undefined
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasAnyFilter()).toBeFalse();
            });

            it(`should verify will return true when there is at least one filter criteria which value is not Nil`, () => {
                // Given
                manager.filterCriteria[FILTER_CRITERIA_F1] = null;
                manager.filterCriteria[FILTER_CRITERIA_F2] = undefined;
                manager.filterCriteria[FILTER_CRITERIA_F4] = 'f4v';
                manager.filterCriteria[FILTER_CRITERIA_F5] = 'f5v';

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: null,
                    [FILTER_CRITERIA_F2]: undefined,
                    [FILTER_CRITERIA_F4]: 'f4v',
                    [FILTER_CRITERIA_F5]: 'f5v'
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasAnyFilter()).toBeTrue();
            });
        });

        describe('|setFilter|', () => {
            it(`should verify won't set filter if it exist and new value is same like stored one`, () => {
                // Given
                const filterValue1 = 'f1v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F1]: filterValue1 } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F1, filterValue1);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).not.toHaveBeenCalled();
                expect(observerSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            });

            it(`should verify will set filter if doesn't exist in manager, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;

                // Then 1
                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F2]: filterValue2 } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F1, filterValue1);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F2]: filterValue2, [FILTER_CRITERIA_F1]: filterValue1 })
                );

                expect(urlStateManagerStub.locationToURL).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will delete filter if exist in manager because provided value is Nil, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // Given
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.filterCriteria[FILTER_CRITERIA_F4] = filterValue4;
                manager.changeUpdateStrategy('replaceToURL');
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F3]: filterValue3,
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F3, null);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F4]: filterValue4 })
                );
                expect(observerSpy).toHaveBeenCalledWith([[FILTER_CRITERIA_F3, null, 'filter']]);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will delete filters multiple times and update URL by default only once`, fakeAsync(() => {
                // Given
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                urlStateManagerStub.navigateToUrl.and.resolveTo(true);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.filterCriteria[FILTER_CRITERIA_F4] = filterValue4;
                manager.changeUpdateStrategy('navigateToUrl');
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F3]: filterValue3,
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F3, null);
                manager.setFilter(FILTER_CRITERIA_F4, null);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F4]: filterValue4 })
                ]);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([FILTER_KEY, null]);
                expect(observerSpy.calls.argsFor(0)).toEqual([[[FILTER_CRITERIA_F3, null, 'filter']]]);
                expect(observerSpy.calls.argsFor(1)).toEqual([[[FILTER_CRITERIA_F4, null, 'filter']]]);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).toHaveBeenCalledTimes(1);
            }));

            it(`should verify won't update URL if updateBrowserUrl parameter is false`, fakeAsync(() => {
                // Given
                const filterValue4 = 'f4v';
                const filterValue5 = 'f5v';
                const mutationObserver1 = new MutationObserver();
                const mutationObserver2 = new MutationObserver();
                const observerError = new Error('observer throws error');
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F4] = filterValue4;
                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F4]: filterValue4 } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F5, filterValue5, false);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F4]: filterValue4,
                    [FILTER_CRITERIA_F5]: filterValue5
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F4]: filterValue4, [FILTER_CRITERIA_F5]: filterValue5 })
                );
                expect(observerSpy1).toHaveBeenCalledWith([[FILTER_CRITERIA_F5, filterValue5, 'filter']]);
                expect(observerSpy2).toHaveBeenCalledWith([[FILTER_CRITERIA_F5, filterValue5, 'filter']]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will log error if update URL with navigateToUrl strategy fails`, fakeAsync(() => {
                // Given
                const filterValue3 = 'f3v';
                const navigateToUrlError = new Error('urlUpdateManager throws error');
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                urlStateManagerStub.navigateToUrl.and.rejectWith(navigateToUrlError);

                // prerequisites manager should have
                manager.changeUpdateStrategy('navigateToUrl');

                // Then 1
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                // When
                manager.setFilter(FILTER_CRITERIA_F3, filterValue3, true);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F3]: filterValue3 } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F3]: filterValue3 })
                );

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).toHaveBeenCalledTimes(1);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to update Browser Url', navigateToUrlError);
            }));
        });

        describe('|deleteFilter|', () => {
            it(`should verify won't delete filter if it doesn't exist`, () => {
                // Given
                const filterValue4 = 'f4v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F4] = filterValue4;
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F4]: filterValue4 } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                const returnedValue = manager.deleteFilter(FILTER_CRITERIA_F2);

                // Then 2
                expect(returnedValue).toBeFalse();
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).not.toHaveBeenCalled();
                expect(observerSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            });

            it(`should verify will delete filter if it exist in manager, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                const returnedValue = manager.deleteFilter(FILTER_CRITERIA_F1);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(returnedValue).toBeTrue();

                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F2]: filterValue2 } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F2]: filterValue2 })
                );
                expect(observerSpy).toHaveBeenCalledWith([[FILTER_CRITERIA_F1, null, 'filter']]);

                expect(urlStateManagerStub.locationToURL).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will delete filters multiple times and update URL by default only once`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                urlStateManagerStub.navigateToUrl.and.resolveTo(true);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;
                manager.changeUpdateStrategy('navigateToUrl');
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                const returnedValue1 = manager.deleteFilter(FILTER_CRITERIA_F1);
                const returnedValue2 = manager.deleteFilter(FILTER_CRITERIA_F2);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(returnedValue1).toBeTrue();
                expect(returnedValue2).toBeTrue();

                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F2]: filterValue2 })
                ]);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([FILTER_KEY, null]);
                expect(observerSpy.calls.argsFor(0)).toEqual([[[FILTER_CRITERIA_F1, null, 'filter']]]);
                expect(observerSpy.calls.argsFor(1)).toEqual([[[FILTER_CRITERIA_F2, null, 'filter']]]);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).toHaveBeenCalledTimes(1);
            }));

            it(`should verify won't update URL if updateBrowserUrl parameter is false`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';
                const mutationObserver1 = new MutationObserver();
                const mutationObserver2 = new MutationObserver();
                const observerError = new Error('observer throws error');
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;
                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);

                // When
                const returnedValue = manager.deleteFilter(FILTER_CRITERIA_F1, false);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(returnedValue).toBeTrue();

                expect(manager.filterCriteria).toEqual({ [FILTER_CRITERIA_F2]: filterValue2 } as Record<FILTER_CRITERIA_UNION, string>);
                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F2]: filterValue2 })
                );
                expect(observerSpy1).toHaveBeenCalledWith([[FILTER_CRITERIA_F1, null, 'filter']]);
                expect(observerSpy2).toHaveBeenCalledWith([[FILTER_CRITERIA_F1, null, 'filter']]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));
        });

        describe('|clearFilters|', () => {
            let observerError: Error;
            let observerSpy1: jasmine.Spy;
            let observerSpy2: jasmine.Spy;
            let consoleErrorSpy: jasmine.Spy;

            beforeEach(() => {
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';

                const mutationObserver1 = new MutationObserver();
                const mutationObserver2 = new MutationObserver();
                observerError = new Error('observer throws error');
                observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;
                manager.filterCriteria[FILTER_CRITERIA_F3] = null;
                manager.filterCriteria[FILTER_CRITERIA_F4] = undefined;
                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2,
                    [FILTER_CRITERIA_F3]: null,
                    [FILTER_CRITERIA_F4]: undefined
                } as Record<FILTER_CRITERIA_UNION, string>);
            });

            it(`should verify will clear all existing filters, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // When
                manager.clearFilters();
                manager.clearFilters();

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(FILTER_KEY, null);

                expect(observerSpy1.calls.count()).toEqual(1);
                expect(observerSpy1.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F2, null, 'filter'],
                        [FILTER_CRITERIA_F3, null, 'filter'],
                        [FILTER_CRITERIA_F4, null, 'filter']
                    ]
                ]);

                expect(observerSpy2.calls.count()).toEqual(1);
                expect(observerSpy2.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F2, null, 'filter'],
                        [FILTER_CRITERIA_F3, null, 'filter'],
                        [FILTER_CRITERIA_F4, null, 'filter']
                    ]
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will clear all existing filters, serialize to URLStateManager, and won't update URL and would notify mutation observers`, fakeAsync(() => {
                // When
                manager.clearFilters(false);
                manager.clearFilters(false);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(FILTER_KEY, null);

                expect(observerSpy1.calls.count()).toEqual(1);
                expect(observerSpy1).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F2, null, 'filter'],
                    [FILTER_CRITERIA_F3, null, 'filter'],
                    [FILTER_CRITERIA_F4, null, 'filter']
                ]);

                expect(observerSpy2.calls.count()).toEqual(1);
                expect(observerSpy2).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F2, null, 'filter'],
                    [FILTER_CRITERIA_F3, null, 'filter'],
                    [FILTER_CRITERIA_F4, null, 'filter']
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will clear all existing filters, serialize to URLStateManager, update URL by default and won't notify mutation observers`, fakeAsync(() => {
                // Given
                manager.changeUpdateStrategy('replaceToURL');

                // When
                manager.clearFilters(true, false);
                manager.clearFilters(true);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(FILTER_KEY, null);

                expect(observerSpy1).not.toHaveBeenCalled();
                expect(observerSpy2).not.toHaveBeenCalled();

                expect(consoleErrorSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));
        });

        describe('|hasSort|', () => {
            it('should verify will return false when there is not such sort criteria', () => {
                // Given
                manager.sortCriteria[SORT_CRITERIA_S1] = 's1v';
                manager.sortCriteria[SORT_CRITERIA_S2] = 's2v';

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: 's1v',
                    [SORT_CRITERIA_S2]: 's2v'
                } as Record<SORT_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasSort(SORT_CRITERIA_S1)).toBeTrue();
                expect(manager.hasSort(SORT_CRITERIA_S2)).toBeTrue();
                expect(manager.hasSort(SORT_CRITERIA_S3)).toBeFalse();
            });

            it(`should verify will return false when there is such sort criteria but it's value is Nil`, () => {
                // Given
                manager.sortCriteria[SORT_CRITERIA_S1] = 's1v';
                manager.sortCriteria[SORT_CRITERIA_S2] = null;
                manager.sortCriteria[SORT_CRITERIA_S3] = undefined;

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: 's1v',
                    [SORT_CRITERIA_S2]: null,
                    [SORT_CRITERIA_S3]: undefined
                } as Record<SORT_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasSort(SORT_CRITERIA_S1)).toBeTrue();
                expect(manager.hasSort(SORT_CRITERIA_S2)).toBeFalse();
                expect(manager.hasSort(SORT_CRITERIA_S3)).toBeFalse();
            });

            it(`should verify will return true when there is such sort criteria and it's value is not Nil`, () => {
                // Given
                manager.sortCriteria[SORT_CRITERIA_S1] = 's1v';
                manager.sortCriteria[SORT_CRITERIA_S2] = 's2v';

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: 's1v',
                    [SORT_CRITERIA_S2]: 's2v'
                } as Record<SORT_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasSort(SORT_CRITERIA_S1)).toBeTrue();
                expect(manager.hasSort(SORT_CRITERIA_S2)).toBeTrue();
                expect(manager.hasSort(SORT_CRITERIA_S3)).toBeFalse();
            });
        });

        describe('|hasAnySort|', () => {
            it('should verify will return false when there is no sort criteria set', () => {
                // Then 1
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                // Then 2
                expect(manager.hasAnySort()).toBeFalse();
            });

            it(`should verify will return false when there are two sort criteria but their value is Nil`, () => {
                // Given
                manager.sortCriteria[SORT_CRITERIA_S1] = null;
                manager.sortCriteria[SORT_CRITERIA_S2] = undefined;

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: null,
                    [SORT_CRITERIA_S2]: undefined
                } as Record<SORT_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasAnySort()).toBeFalse();
            });

            it(`should verify will return true when there is at least one sort criteria which value is not Nil`, () => {
                // Given
                manager.sortCriteria[SORT_CRITERIA_S1] = null;
                manager.sortCriteria[SORT_CRITERIA_S2] = undefined;
                manager.sortCriteria[SORT_CRITERIA_S3] = 's3v';

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: null,
                    [SORT_CRITERIA_S2]: undefined,
                    [SORT_CRITERIA_S3]: 's3v'
                } as Record<SORT_CRITERIA_UNION, string>);

                // When/Then 2
                expect(manager.hasAnySort()).toBeTrue();
            });
        });

        describe('|setSort|', () => {
            it(`should verify won't set sort if it exist and new value is same like stored one`, () => {
                // Given
                const sortValue1 = 's1v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S1]: sortValue1 } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S1, sortValue1);

                // Then 2
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S1]: sortValue1 } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).not.toHaveBeenCalled();

                expect(observerSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            });

            it(`should verify will set sort if doesn't exist in manager, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // Given
                const sortValue1 = 's1v';
                const sortValue2 = 's2v';

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;

                // Then 1
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S2]: sortValue2 } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S1, sortValue1);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: sortValue2, [SORT_CRITERIA_S1]: sortValue1 })
                );

                expect(urlStateManagerStub.locationToURL).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will delete sort if exist in manager because provided value is Nil, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // Given
                const sortValue1 = 's1v';
                const sortValue2 = 's2v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.changeUpdateStrategy('replaceToURL');
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S1, null);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S2]: sortValue2 } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: sortValue2 })
                );

                expect(observerSpy).toHaveBeenCalledWith([[SORT_CRITERIA_S1, null, 'sort']]);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will delete sort multiple times and update URL by default only once`, fakeAsync(() => {
                // Given
                const sortValue1 = 's1v';
                const sortValue2 = 's2v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                urlStateManagerStub.navigateToUrl.and.resolveTo(true);

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;

                manager.changeUpdateStrategy('navigateToUrl');
                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S1, null);
                manager.setSort(SORT_CRITERIA_S2, null);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: sortValue2 })
                ]);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([SORT_KEY, null]);

                expect(observerSpy.calls.argsFor(0)).toEqual([[[SORT_CRITERIA_S1, null, 'sort']]]);
                expect(observerSpy.calls.argsFor(1)).toEqual([[[SORT_CRITERIA_S2, null, 'sort']]]);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).toHaveBeenCalledTimes(1);
            }));

            it(`should verify won't update URL if updateBrowserUrl parameter is false`, fakeAsync(() => {
                // Given
                const sortValue1 = 's1v';
                const sortValue2 = 's2v';

                const mutationObserver1 = new MutationObserver();
                const mutationObserver2 = new MutationObserver();

                const observerError = new Error('observer throws error');
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S1]: sortValue1 } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S2, sortValue2, false);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S1]: sortValue1, [SORT_CRITERIA_S2]: sortValue2 })
                );

                expect(observerSpy1).toHaveBeenCalledWith([[SORT_CRITERIA_S2, sortValue2, 'sort']]);
                expect(observerSpy2).toHaveBeenCalledWith([[SORT_CRITERIA_S2, sortValue2, 'sort']]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will log error if update URL with navigateToUrl strategy fails`, fakeAsync(() => {
                // Given
                const sortValue1 = 's1v';
                const navigateToUrlError = new Error('urlUpdateManager throws error');
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                urlStateManagerStub.navigateToUrl.and.rejectWith(navigateToUrlError);

                // prerequisites manager should have
                manager.changeUpdateStrategy('navigateToUrl');

                // Then 1
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.setSort(SORT_CRITERIA_S1, sortValue1, true);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then 2
                expect(manager.sortCriteria).toEqual({ [SORT_CRITERIA_S1]: sortValue1 } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S1]: sortValue1 })
                );

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).toHaveBeenCalledTimes(1);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to update Browser Url', navigateToUrlError);
            }));
        });

        describe('|clearSort|', () => {
            let observerError: Error;
            let observerSpy1: jasmine.Spy;
            let observerSpy2: jasmine.Spy;
            let consoleErrorSpy: jasmine.Spy;

            beforeEach(() => {
                const sortValue1 = 's1v';

                const mutationObserver1 = new MutationObserver();
                const mutationObserver2 = new MutationObserver();
                observerError = new Error('observer throws error');
                observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;
                manager.sortCriteria[SORT_CRITERIA_S2] = null;
                manager.sortCriteria[SORT_CRITERIA_S3] = undefined;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: null,
                    [SORT_CRITERIA_S3]: undefined
                } as Record<SORT_CRITERIA_UNION, string>);
            });

            it(`should verify will clear all existing sort, serialize to URLStateManager, update URL by default and notify mutation observers`, fakeAsync(() => {
                // When
                manager.clearSort();
                manager.clearSort();

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(SORT_KEY, null);

                expect(observerSpy1.calls.count()).toEqual(1);
                expect(observerSpy1.calls.argsFor(0)).toEqual([
                    [
                        [SORT_CRITERIA_S1, null, 'sort'],
                        [SORT_CRITERIA_S2, null, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort']
                    ]
                ]);

                expect(observerSpy2.calls.count()).toEqual(1);
                expect(observerSpy2.calls.argsFor(0)).toEqual([
                    [
                        [SORT_CRITERIA_S1, null, 'sort'],
                        [SORT_CRITERIA_S2, null, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort']
                    ]
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).toHaveBeenCalledTimes(1);
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will clear all existing sort, serialize to URLStateManager, and won't update URL and would notify mutation observers`, fakeAsync(() => {
                // When
                manager.clearSort(false);
                manager.clearSort(false);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(SORT_KEY, null);

                expect(observerSpy1.calls.count()).toEqual(1);
                expect(observerSpy1).toHaveBeenCalledWith([
                    [SORT_CRITERIA_S1, null, 'sort'],
                    [SORT_CRITERIA_S2, null, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort']
                ]);

                expect(observerSpy2.calls.count()).toEqual(1);
                expect(observerSpy2).toHaveBeenCalledWith([
                    [SORT_CRITERIA_S1, null, 'sort'],
                    [SORT_CRITERIA_S2, null, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort']
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith('FiltersManager: Failed to notify mutation observers', observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will clear all existing sort, serialize to URLStateManager, update URL by default and won't notify mutation observers`, fakeAsync(() => {
                // Given
                manager.changeUpdateStrategy('replaceToURL');

                // When
                manager.clearSort(true, false);
                manager.clearSort(true);

                // wait virtually 1s because navigation is debounced for 300ms by default
                tick(1000);

                // Then
                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).toHaveBeenCalledWith(SORT_KEY, null);

                expect(observerSpy1).not.toHaveBeenCalled();
                expect(observerSpy2).not.toHaveBeenCalled();

                expect(consoleErrorSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));
        });

        describe('|clear|', () => {
            it('should verify will invoke correct methods with correct parameters', () => {
                // Given
                const clearFiltersSpy = spyOn(manager, 'clearFilters').and.callFake(CallFake);
                const clearSortSpy = spyOn(manager, 'clearSort').and.callFake(CallFake);

                // When 1
                manager.clear();

                // When 2
                manager.clear(true, true);

                // When 3
                manager.clear(false, false);

                // Then
                expect(clearFiltersSpy.calls.argsFor(0)).toEqual([true, true]);
                expect(clearSortSpy.calls.argsFor(0)).toEqual([true, true]);

                expect(clearFiltersSpy.calls.argsFor(1)).toEqual([true, true]);
                expect(clearSortSpy.calls.argsFor(1)).toEqual([true, true]);

                expect(clearFiltersSpy.calls.argsFor(2)).toEqual([false, false]);
                expect(clearSortSpy.calls.argsFor(2)).toEqual([false, false]);
            });
        });

        describe('|bulkUpdate|', () => {
            it(`should verify if value is Nil won't execute anything`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v';
                const filterValue2 = 'f2v';
                const sortValue1 = 's1v';
                const sortValue2 = 's2v';
                const mutationObserver = new MutationObserver();
                const observerSpy = spyOn(mutationObserver, 'observer').and.callThrough();

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F2] = filterValue2;

                manager.sortCriteria[SORT_CRITERIA_S1] = sortValue1;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;

                manager.registerMutationObserver(mutationObserver.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate(null);

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F2]: filterValue2
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S1]: sortValue1,
                    [SORT_CRITERIA_S2]: sortValue2
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam).not.toHaveBeenCalled();

                expect(observerSpy).not.toHaveBeenCalled();

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will update values from Array of key-value (criteria-value) tuples, filter and sort`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v,f11v';
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v,f44v,f444v';
                const sortValue1 = 's1v';
                const sortValue2 = '-1';
                const sortValue3 = 's3v';
                const sortValue4 = 's4v';

                const observerError = new Error('observer throws error');

                const mutationObserver1 = new MutationObserver();
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.callThrough();
                const mutationObserver2 = new MutationObserver();
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const mutationObserver3 = new MutationObserver();
                const observerSpy3 = spyOn(mutationObserver3, 'observer').and.throwError(observerError);

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.sortCriteria[SORT_CRITERIA_S3] = sortValue3;
                manager.sortCriteria[SORT_CRITERIA_S4] = sortValue4;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);
                manager.registerMutationObserver(mutationObserver3.observer);

                manager.deleteMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: filterValue3
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: sortValue2,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate([
                    [SORT_CRITERIA_S1, sortValue1, 'sort'],
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F3, filterValue3, 'filter'],
                    [SORT_CRITERIA_S3, null, 'sort'],
                    [FILTER_CRITERIA_F2, null, 'filter'],
                    ['someSort', '-1', 'sort'] as unknown as KeyValueTuple<SORT_CRITERIA_UNION, string>,
                    [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                    ['someFilter', 'testValue', 'filter'] as unknown as KeyValueTuple<FILTER_CRITERIA_UNION, string>,
                    [SORT_CRITERIA_S2, sortValue2, 'sort'],
                    [SORT_CRITERIA_S4, '', 'sort']
                ]);

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F3]: filterValue3,
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: parseInt(sortValue2, 10) as unknown,
                    [SORT_CRITERIA_S1]: sortValue1
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F3]: filterValue3, [FILTER_CRITERIA_F4]: filterValue4 })
                ]);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: parseInt(sortValue2, 10), [SORT_CRITERIA_S1]: sortValue1 })
                ]);

                expect(observerSpy1).toHaveBeenCalledTimes(1);
                expect(observerSpy1).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                    [SORT_CRITERIA_S1, sortValue1, 'sort'],
                    [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort'],
                    [SORT_CRITERIA_S4, null, 'sort']
                ]);

                expect(observerSpy2).not.toHaveBeenCalled();

                expect(observerSpy3).toHaveBeenCalledTimes(1);
                expect(observerSpy3).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                    [SORT_CRITERIA_S1, sortValue1, 'sort'],
                    [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort'],
                    [SORT_CRITERIA_S4, null, 'sort']
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith(`FiltersManager: Failed to notify mutation observers`, observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will update values from Array of key-value (criteria-value) tuples, filter and sort and clear previous values`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v,f11v';
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v,f44v,f444v';
                const sortValue1 = 's1v';
                const sortValue2 = '-1';
                const sortValue3 = 's3v';
                const sortValue4 = 's4v';

                const observerError = new Error('observer throws error');

                const mutationObserver1 = new MutationObserver();
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.callThrough();
                const mutationObserver2 = new MutationObserver();
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const mutationObserver3 = new MutationObserver();
                const observerSpy3 = spyOn(mutationObserver3, 'observer').and.throwError(observerError);

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.sortCriteria[SORT_CRITERIA_S3] = sortValue3;
                manager.sortCriteria[SORT_CRITERIA_S4] = sortValue4;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);
                manager.registerMutationObserver(mutationObserver3.observer);

                manager.deleteMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: filterValue3
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: sortValue2,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate(
                    [
                        [SORT_CRITERIA_S1, sortValue1, 'sort'],
                        [FILTER_CRITERIA_F3, filterValue3, 'filter'],
                        [FILTER_CRITERIA_F2, null, 'filter'],
                        ['someSort', '-1', 'sort'] as unknown as KeyValueTuple<SORT_CRITERIA_UNION, string>,
                        [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                        ['someFilter', 'testValue', 'filter'] as unknown as KeyValueTuple<FILTER_CRITERIA_UNION, string>,
                        [SORT_CRITERIA_S2, sortValue2, 'sort'],
                        [SORT_CRITERIA_S4, '', 'sort']
                    ],
                    true
                );

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F3]: filterValue3,
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: parseInt(sortValue2, 10) as unknown,
                    [SORT_CRITERIA_S1]: sortValue1
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F3]: filterValue3, [FILTER_CRITERIA_F4]: filterValue4 })
                ]);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: parseInt(sortValue2, 10), [SORT_CRITERIA_S1]: sortValue1 })
                ]);

                expect(observerSpy1).toHaveBeenCalledTimes(1);
                expect(observerSpy1).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                    [SORT_CRITERIA_S1, sortValue1, 'sort'],
                    [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort'],
                    [SORT_CRITERIA_S4, null, 'sort']
                ]);

                expect(observerSpy2).not.toHaveBeenCalled();

                expect(observerSpy3).toHaveBeenCalledTimes(1);
                expect(observerSpy3).toHaveBeenCalledWith([
                    [FILTER_CRITERIA_F1, null, 'filter'],
                    [FILTER_CRITERIA_F4, filterValue4, 'filter'],
                    [SORT_CRITERIA_S1, sortValue1, 'sort'],
                    [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                    [SORT_CRITERIA_S3, null, 'sort'],
                    [SORT_CRITERIA_S4, null, 'sort']
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith(`FiltersManager: Failed to notify mutation observers`, observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will update values from object of key-value (criteria-value) properties, filter and sort`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v,f11v';
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v,f44v,f444v';
                const sortValue1 = 's1v';
                const sortValue2 = '-1';
                const sortValue3 = 's3v';
                const sortValue4 = 's4v';

                const observerError = new Error('observer throws error');

                const mutationObserver1 = new MutationObserver();
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const mutationObserver2 = new MutationObserver();
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const mutationObserver3 = new MutationObserver();
                const observerSpy3 = spyOn(mutationObserver3, 'observer').and.callThrough();

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.sortCriteria[SORT_CRITERIA_S3] = sortValue3;
                manager.sortCriteria[SORT_CRITERIA_S4] = sortValue4;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);
                manager.registerMutationObserver(mutationObserver3.observer);

                manager.deleteMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: filterValue3
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: sortValue2,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate({
                    [FILTER_KEY]: JSON.stringify({
                        [FILTER_CRITERIA_F3]: `${filterValue3}10`,
                        [FILTER_CRITERIA_F4]: undefined,
                        someFilter: 'testValue'
                    }),
                    [SORT_KEY]: JSON.stringify({
                        [SORT_CRITERIA_S1]: sortValue1,
                        someSort: -1,
                        [SORT_CRITERIA_S2]: sortValue2,
                        [SORT_CRITERIA_S4]: undefined
                    })
                });

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: `${filterValue3}10`
                } as Record<FILTER_CRITERIA_UNION, string>);

                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: parseInt(sortValue2, 10) as unknown,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4,
                    [SORT_CRITERIA_S1]: sortValue1
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({
                        [FILTER_CRITERIA_F1]: filterValue1,
                        [FILTER_CRITERIA_F3]: `${filterValue3}10`
                    })
                ]);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([
                    SORT_KEY,
                    JSON.stringify({
                        [SORT_CRITERIA_S2]: parseInt(sortValue2, 10),
                        [SORT_CRITERIA_S3]: sortValue3,
                        [SORT_CRITERIA_S4]: sortValue4,
                        [SORT_CRITERIA_S1]: sortValue1
                    })
                ]);

                expect(observerSpy1).toHaveBeenCalledTimes(2);
                expect(observerSpy1.calls.argsFor(0)).toEqual([[[FILTER_CRITERIA_F3, `${filterValue3}10`, 'filter']]]);
                expect(observerSpy1.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S1, sortValue1, 'sort'],
                        [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort']
                    ]
                ]);

                expect(observerSpy2).not.toHaveBeenCalled();

                expect(observerSpy3).toHaveBeenCalledTimes(2);
                expect(observerSpy3.calls.argsFor(0)).toEqual([[[FILTER_CRITERIA_F3, `${filterValue3}10`, 'filter']]]);
                expect(observerSpy3.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S1, sortValue1, 'sort'],
                        [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort']
                    ]
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith(`FiltersManager: Failed to notify mutation observers`, observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will update values from object of key-value (criteria-value) properties, filter and sort and clear previous values`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v,f11v';
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v,f44v,f444v';
                const sortValue1 = 's1v';
                const sortValue2 = '-1';
                const sortValue3 = 's3v';
                const sortValue4 = 's4v';

                const observerError = new Error('observer throws error');

                const mutationObserver1 = new MutationObserver();
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const mutationObserver2 = new MutationObserver();
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const mutationObserver3 = new MutationObserver();
                const observerSpy3 = spyOn(mutationObserver3, 'observer').and.callThrough();

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.sortCriteria[SORT_CRITERIA_S3] = sortValue3;
                manager.sortCriteria[SORT_CRITERIA_S4] = sortValue4;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);
                manager.registerMutationObserver(mutationObserver3.observer);

                manager.deleteMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: filterValue3
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: sortValue2,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate(
                    {
                        [FILTER_KEY]: JSON.stringify({
                            [FILTER_CRITERIA_F3]: `${filterValue3}10`,
                            [FILTER_CRITERIA_F4]: filterValue4,
                            someFilter: 'testValue'
                        }),
                        [SORT_KEY]: JSON.stringify({
                            [SORT_CRITERIA_S1]: sortValue1,
                            someSort: -1,
                            [SORT_CRITERIA_S2]: sortValue2,
                            [SORT_CRITERIA_S4]: undefined
                        })
                    },
                    true
                );

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F3]: `${filterValue3}10`,
                    [FILTER_CRITERIA_F4]: filterValue4
                } as Record<FILTER_CRITERIA_UNION, string>);

                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: parseInt(sortValue2, 10) as unknown,
                    [SORT_CRITERIA_S1]: sortValue1
                } as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([
                    FILTER_KEY,
                    JSON.stringify({ [FILTER_CRITERIA_F3]: `${filterValue3}10`, [FILTER_CRITERIA_F4]: filterValue4 })
                ]);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([
                    SORT_KEY,
                    JSON.stringify({ [SORT_CRITERIA_S2]: parseInt(sortValue2, 10), [SORT_CRITERIA_S1]: sortValue1 })
                ]);

                expect(observerSpy1).toHaveBeenCalledTimes(2);
                expect(observerSpy1.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F3, `${filterValue3}10`, 'filter'],
                        [FILTER_CRITERIA_F4, filterValue4, 'filter']
                    ]
                ]);
                expect(observerSpy1.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S1, sortValue1, 'sort'],
                        [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort'],
                        [SORT_CRITERIA_S4, null, 'sort']
                    ]
                ]);

                expect(observerSpy2).not.toHaveBeenCalled();

                expect(observerSpy3).toHaveBeenCalledTimes(2);
                expect(observerSpy3.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F3, `${filterValue3}10`, 'filter'],
                        [FILTER_CRITERIA_F4, filterValue4, 'filter']
                    ]
                ]);
                expect(observerSpy3.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S1, sortValue1, 'sort'],
                        [SORT_CRITERIA_S2, parseInt(sortValue2, 10) as unknown as string, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort'],
                        [SORT_CRITERIA_S4, null, 'sort']
                    ]
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith(`FiltersManager: Failed to notify mutation observers`, observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));

            it(`should verify will update values from object of key-value (criteria-value) properties, filter and sort are missing and clear previous values`, fakeAsync(() => {
                // Given
                const filterValue1 = 'f1v,f11v';
                const filterValue3 = 'f3v';
                const filterValue4 = 'f4v,f44v,f444v';
                const sortValue1 = 's1v';
                const sortValue2 = '-1';
                const sortValue3 = 's3v';
                const sortValue4 = 's4v';

                const observerError = new Error('observer throws error');

                const mutationObserver1 = new MutationObserver();
                const observerSpy1 = spyOn(mutationObserver1, 'observer').and.throwError(observerError);
                const mutationObserver2 = new MutationObserver();
                const observerSpy2 = spyOn(mutationObserver2, 'observer').and.callThrough();
                const mutationObserver3 = new MutationObserver();
                const observerSpy3 = spyOn(mutationObserver3, 'observer').and.callThrough();

                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);

                // prerequisites manager should have
                manager.filterCriteria[FILTER_CRITERIA_F1] = filterValue1;
                manager.filterCriteria[FILTER_CRITERIA_F3] = filterValue3;
                manager.sortCriteria[SORT_CRITERIA_S2] = sortValue2;
                manager.sortCriteria[SORT_CRITERIA_S3] = sortValue3;
                manager.sortCriteria[SORT_CRITERIA_S4] = sortValue4;

                manager.registerMutationObserver(mutationObserver1.observer);
                manager.registerMutationObserver(mutationObserver2.observer);
                manager.registerMutationObserver(mutationObserver3.observer);

                manager.deleteMutationObserver(mutationObserver2.observer);

                // Then 1
                expect(manager.filterCriteria).toEqual({
                    [FILTER_CRITERIA_F1]: filterValue1,
                    [FILTER_CRITERIA_F3]: filterValue3
                } as Record<FILTER_CRITERIA_UNION, string>);
                expect(manager.sortCriteria).toEqual({
                    [SORT_CRITERIA_S2]: sortValue2,
                    [SORT_CRITERIA_S3]: sortValue3,
                    [SORT_CRITERIA_S4]: sortValue4
                } as Record<SORT_CRITERIA_UNION, string>);

                // When
                manager.bulkUpdate({} as Record<typeof FILTER_KEY | typeof SORT_KEY, string>, true);

                tick(1000);

                // Then 2
                expect(manager.filterCriteria).toEqual({} as Record<FILTER_CRITERIA_UNION, string>);

                expect(manager.sortCriteria).toEqual({} as Record<SORT_CRITERIA_UNION, string>);

                expect(urlStateManagerStub.setQueryParam.calls.argsFor(0)).toEqual([FILTER_KEY, null]);
                expect(urlStateManagerStub.setQueryParam.calls.argsFor(1)).toEqual([SORT_KEY, null]);

                expect(observerSpy1).toHaveBeenCalledTimes(2);
                expect(observerSpy1.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F3, null, 'filter']
                    ]
                ]);
                expect(observerSpy1.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S2, null, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort'],
                        [SORT_CRITERIA_S4, null, 'sort']
                    ]
                ]);

                expect(observerSpy2).not.toHaveBeenCalled();

                expect(observerSpy3).toHaveBeenCalledTimes(2);
                expect(observerSpy3.calls.argsFor(0)).toEqual([
                    [
                        [FILTER_CRITERIA_F1, null, 'filter'],
                        [FILTER_CRITERIA_F3, null, 'filter']
                    ]
                ]);
                expect(observerSpy3.calls.argsFor(1)).toEqual([
                    [
                        [SORT_CRITERIA_S2, null, 'sort'],
                        [SORT_CRITERIA_S3, null, 'sort'],
                        [SORT_CRITERIA_S4, null, 'sort']
                    ]
                ]);

                expect(consoleErrorSpy).toHaveBeenCalledWith(`FiltersManager: Failed to notify mutation observers`, observerError);

                expect(urlStateManagerStub.locationToURL).not.toHaveBeenCalled();
                expect(urlStateManagerStub.replaceToUrl).not.toHaveBeenCalled();
                expect(urlStateManagerStub.navigateToUrl).not.toHaveBeenCalled();
            }));
        });
    });
});
