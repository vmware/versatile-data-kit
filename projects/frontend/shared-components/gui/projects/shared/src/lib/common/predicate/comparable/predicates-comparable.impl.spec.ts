

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CallFake } from '../../../unit-testing';

import { Comparable, Predicate } from '../../interfaces';

import { PredicatesComparable } from './predicates-comparable.impl';

class ComparableStub implements Comparable {
    public readonly value: any;

    constructor(value: any) {
        this.value = value;
    }

    compare(_comparable: Comparable): number {
        return 0;
    }

    equal(_comparable: Comparable): boolean {
        return true;
    }

    like(_comparable: Comparable): boolean {
        return true;
    }

    notEqual(_comparable: Comparable): boolean {
        return false;
    }

    isNil(): boolean {
        return false;
    }

    notNil(): boolean {
        return true;
    }

    greaterThan(_comparable: Comparable): boolean {
        return false;
    }

    greaterThanInclusive(_comparable: Comparable): boolean {
        return false;
    }

    lessThan(_comparable: Comparable): boolean {
        return false;
    }

    lessThanInclusive(_comparable: Comparable): boolean {
        return false;
    }
}

class PredicateEqualStub implements Predicate {
    comparable: ComparableStub;

    constructor(comparable: ComparableStub) {
        this.comparable = comparable;
    }

    evaluate(comparable: Comparable): boolean {
        return this.comparable.equal(comparable);
    }
}

describe('PredicatesComparable', () => {
    let predicate1: Predicate;
    let predicate2: Predicate;
    let predicate3: Predicate;

    beforeEach(() => {
        predicate1 = new PredicateEqualStub(new ComparableStub('A'));
        predicate2 = new PredicateEqualStub(new ComparableStub('B'));
        predicate3 = new PredicateEqualStub(new ComparableStub('1'));
    });

    it('should verify instance is created', () => {
        // When
        const instance = new PredicatesComparable(predicate1, predicate2);

        // Then
        expect(instance).toBeDefined();
    });

    it('should verify value is correctly assigned', () => {
        // When
        const instance = new PredicatesComparable(predicate1, predicate2);

        // Then
        expect(instance.value[0]).toBe(predicate1);
        expect(instance.value[1]).toBe(predicate2);
    });

    describe('Statics::', () => {
        describe('Methods::()', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // When
                    const instance = PredicatesComparable.of(predicate1, predicate2);

                    // Then
                    expect(instance).toBeDefined();
                    expect(instance).toBeInstanceOf(PredicatesComparable);
                    expect(instance.value[0]).toBe(predicate1);
                    expect(instance.value[1]).toBe(predicate2);
                });
            });
        });
    });

    describe('Methods::()', () => {
        let predicatesComparable: PredicatesComparable;
        let injectedComparable: ComparableStub;
        let consoleWarnSpy: jasmine.Spy;

        beforeEach(() => {
            predicatesComparable = PredicatesComparable.of(predicate1, predicate2);
            injectedComparable = new ComparableStub('C');
            consoleWarnSpy = spyOn(console, 'warn').and.callFake(CallFake);
        });

        describe('|compare|', () => {
            it('should verify will return -1 and log warn to console', () => {
                // When
                const comparison = predicatesComparable.compare(injectedComparable);

                // Then
                expect(comparison).toEqual(-1);
                expect(consoleWarnSpy).toHaveBeenCalledWith('PredicatesComparable, unsupported comparison.');
            });
        });

        describe('|isNil|', () => {
            it('should verify will return false all the time', () => {
                // Given
                const c1 = PredicatesComparable.of(null);
                const c2 = PredicatesComparable.of(undefined);
                const c3 = PredicatesComparable.of(predicate1);

                // When
                const r1 = c1.isNil();
                const r2 = c2.isNil();
                const r3 = c3.isNil();

                // Then
                expect(r1).toBeFalse();
                expect(r2).toBeFalse();
                expect(r3).toBeFalse();
            });
        });

        describe('|notNil|', () => {
            it('should verify will return true all the time', () => {
                // Given
                const c1 = PredicatesComparable.of(null);
                const c2 = PredicatesComparable.of(undefined);
                const c3 = PredicatesComparable.of(predicate1);

                // When
                const r1 = c1.notNil();
                const r2 = c2.notNil();
                const r3 = c3.notNil();

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeTrue();
                expect(r3).toBeTrue();
            });
        });

        describe('|like|', () => {
            it('should verify will return true if one or more predicates return true, otherwise false', () => {
                // Given
                const predicate1EvaluateSpy = spyOn(predicate1, 'evaluate').and.returnValues(false, false);
                const predicate2EvaluateSpy = spyOn(predicate2, 'evaluate').and.returnValues(true, false);
                const predicate3EvaluateSpy = spyOn(predicate3, 'evaluate').and.returnValues(false);
                const comparableStub = new ComparableStub('D');
                predicatesComparable = PredicatesComparable.of(predicate1, predicate2, predicate3);

                // When
                const r1 = predicatesComparable.like(injectedComparable);
                const r2 = predicatesComparable.like(comparableStub);

                // Then
                expect(r1).toBeTrue();
                expect(predicate1EvaluateSpy.calls.argsFor(0)).toEqual([injectedComparable]);
                expect(predicate2EvaluateSpy.calls.argsFor(0)).toEqual([injectedComparable]);

                expect(r2).toBeFalse();
                expect(predicate1EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub]);
                expect(predicate2EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub]);
                expect(predicate3EvaluateSpy.calls.argsFor(0)).toEqual([comparableStub]);

                expect(predicate1EvaluateSpy).toHaveBeenCalledTimes(2);
                expect(predicate2EvaluateSpy).toHaveBeenCalledTimes(2);
                expect(predicate3EvaluateSpy).toHaveBeenCalledTimes(1);
            });
        });

        describe('|equal|', () => {
            it('should verify will return true if all predicates return true, otherwise false', () => {
                // Given
                const predicate1EvaluateSpy = spyOn(predicate1, 'evaluate').and.returnValues(true, false, true);
                const predicate2EvaluateSpy = spyOn(predicate2, 'evaluate').and.returnValues(false, true);
                const predicate3EvaluateSpy = spyOn(predicate3, 'evaluate').and.returnValues(true);
                const comparableStub1 = new ComparableStub('F');
                const comparableStub2 = new ComparableStub('G');
                predicatesComparable = PredicatesComparable.of(predicate1, predicate2, predicate3);

                // When
                const r1 = predicatesComparable.equal(injectedComparable);
                const r2 = predicatesComparable.equal(comparableStub1);
                const r3 = predicatesComparable.equal(comparableStub2);

                // Then
                expect(r1).toBeFalse();
                expect(predicate1EvaluateSpy.calls.argsFor(0)).toEqual([injectedComparable]);
                expect(predicate2EvaluateSpy.calls.argsFor(0)).toEqual([injectedComparable]);

                expect(r2).toBeFalse();
                expect(predicate1EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub1]);

                expect(r3).toBeTrue();
                expect(predicate1EvaluateSpy.calls.argsFor(2)).toEqual([comparableStub2]);
                expect(predicate2EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub2]);
                expect(predicate3EvaluateSpy.calls.argsFor(0)).toEqual([comparableStub2]);

                expect(predicate1EvaluateSpy).toHaveBeenCalledTimes(3);
                expect(predicate2EvaluateSpy).toHaveBeenCalledTimes(2);
                expect(predicate3EvaluateSpy).toHaveBeenCalledTimes(1);
            });
        });

        describe('|notEqual|', () => {
            it('should verify will return true if one or more predicates return false, otherwise false', () => {
                // Given
                const predicate1EvaluateSpy = spyOn(predicate1, 'evaluate').and.returnValues(false, true, true);
                const predicate2EvaluateSpy = spyOn(predicate2, 'evaluate').and.returnValues(false, true);
                const predicate3EvaluateSpy = spyOn(predicate3, 'evaluate').and.returnValues(true);
                const comparableStub1 = new ComparableStub('H');
                const comparableStub2 = new ComparableStub('I');
                predicatesComparable = PredicatesComparable.of(predicate1, predicate2, predicate3);

                // When
                const r1 = predicatesComparable.notEqual(injectedComparable);
                const r2 = predicatesComparable.notEqual(comparableStub1);
                const r3 = predicatesComparable.notEqual(comparableStub2);

                // Then
                expect(r1).toBeTrue();
                expect(predicate1EvaluateSpy.calls.argsFor(0)).toEqual([injectedComparable]);

                expect(r2).toBeTrue();
                expect(predicate1EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub1]);
                expect(predicate2EvaluateSpy.calls.argsFor(0)).toEqual([comparableStub1]);

                expect(r3).toBeFalse();
                expect(predicate1EvaluateSpy.calls.argsFor(2)).toEqual([comparableStub2]);
                expect(predicate2EvaluateSpy.calls.argsFor(1)).toEqual([comparableStub2]);
                expect(predicate3EvaluateSpy.calls.argsFor(0)).toEqual([comparableStub2]);

                expect(predicate1EvaluateSpy).toHaveBeenCalledTimes(3);
                expect(predicate2EvaluateSpy).toHaveBeenCalledTimes(2);
                expect(predicate3EvaluateSpy).toHaveBeenCalledTimes(1);
            });
        });

        describe('|lessThan|', () => {
            it('should verify will return -1 and log warn to console', () => {
                // When
                const comparison = predicatesComparable.lessThan(injectedComparable);

                // Then
                expect(comparison).toBeFalse();
                expect(consoleWarnSpy).toHaveBeenCalledWith('PredicatesComparable, unsupported comparison.');
            });
        });

        describe('|lessThanInclusive|', () => {
            it('should verify will return -1 and log warn to console', () => {
                // When
                const comparison = predicatesComparable.lessThanInclusive(injectedComparable);

                // Then
                expect(comparison).toBeFalse();
                expect(consoleWarnSpy).toHaveBeenCalledWith('PredicatesComparable, unsupported comparison.');
            });
        });

        describe('|greaterThan|', () => {
            it('should verify will return -1 and log warn to console', () => {
                // When
                const comparison = predicatesComparable.greaterThan(injectedComparable);

                // Then
                expect(comparison).toBeFalse();
                expect(consoleWarnSpy).toHaveBeenCalledWith('PredicatesComparable, unsupported comparison.');
            });
        });

        describe('|greaterThanInclusive|', () => {
            it('should verify will return -1 and log warn to console', () => {
                // When
                const comparison = predicatesComparable.greaterThanInclusive(injectedComparable);

                // Then
                expect(comparison).toBeFalse();
                expect(consoleWarnSpy).toHaveBeenCalledWith('PredicatesComparable, unsupported comparison.');
            });
        });
    });
});
