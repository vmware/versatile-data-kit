

import { CallFake } from '../../../unit-testing';

import { Comparable, Predicate } from '../../interfaces';

import { PredicatesComparable } from '../comparable';

import { CompoundPredicate } from './base-compound.predicate';
import { Or } from './or.predicate';

describe('Or', () => {
    it('should verify instance is created from one predicate', () => {
        // Given
        const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };

        // When
        const instance = new Or(predicate1);

        // Then
        expect(instance).toBeDefined();
        expect(instance).toBeInstanceOf(CompoundPredicate);
        expect(instance.comparable).toBeInstanceOf(PredicatesComparable);
        expect(instance.comparable.value[0]).toBe(predicate1);
    });

    it('should verify instance is created from predicates', () => {
        // Given
        const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
        const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };

        // When
        const instance = new Or(predicate1, predicate2);

        // Then
        expect(instance).toBeDefined();
        expect(instance).toBeInstanceOf(CompoundPredicate);
        expect(instance.comparable).toBeInstanceOf(PredicatesComparable);
        expect(instance.comparable.value[0]).toBe(predicate1);
        expect(instance.comparable.value[1]).toBe(predicate2);
    });

    it('should verify instance is created from comparable', () => {
        // Given
        const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
        const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
        const comparable = new PredicatesComparable(predicate1, predicate2);

        // When
        const instance = new Or(comparable);

        // Then
        expect(instance).toBeDefined();
        expect(instance).toBeInstanceOf(CompoundPredicate);
        expect(instance.comparable).toBe(comparable);
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance from predicates', () => {
                    // Given
                    const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                    const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };

                    // When
                    const instance = Or.of(predicate1, predicate2);

                    // Then
                    expect(instance).toBeInstanceOf(Or);
                    expect(instance).toBeInstanceOf(CompoundPredicate);
                    expect(instance.comparable).toBeInstanceOf(PredicatesComparable);
                    expect(instance.comparable.value[0]).toBe(predicate1);
                    expect(instance.comparable.value[1]).toBe(predicate2);
                });

                it('should verify factory method will create instance from comparable', () => {
                    // Given
                    const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                    const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                    const comparable = new PredicatesComparable(predicate1, predicate2);

                    // When
                    const instance = Or.of(comparable);

                    // Then
                    expect(instance).toBeInstanceOf(Or);
                    expect(instance).toBeInstanceOf(CompoundPredicate);
                    expect(instance.comparable).toBe(comparable);
                });
            });
        });
    });

    describe('Methods::', () => {
        describe('|evaluate|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const comparableLikeSpy = spyOn(PredicatesComparable.prototype, 'like').and.returnValue(true);
                const predicate1: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                const predicate2: Predicate = { comparable: {} as Comparable, evaluate: CallFake };
                const predicatesComparable = new PredicatesComparable(predicate1, predicate2);
                const instance = new Or(predicatesComparable);
                const standardComparable = {} as Comparable;

                // When
                const result = instance.evaluate(standardComparable);

                // Then
                expect(result).toBeTrue();
                expect(comparableLikeSpy).toHaveBeenCalledWith(standardComparable);
            });
        });
    });
});
