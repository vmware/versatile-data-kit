

import { Comparable } from '../../interfaces';

import { ComparableImpl } from '../comparable';

import { Equal } from './equal.predicate';

describe('Equal', () => {
    let v1: string;
    let v2: string;
    let v3: string;

    let c1: Comparable;
    let c2: Comparable;
    let c3: Comparable;

    beforeEach(() => {
        v1 = 'Taurus';
        v2 = 'Taurus';
        v3 = 'Super Collider';

        c1 = ComparableImpl.of(v1);
        c2 = ComparableImpl.of(v2);
        c3 = ComparableImpl.of(v3);
    });

    it('should verify instance is created', () => {
        // When
        const p = new Equal(c1);

        // Then
        expect(p).toBeDefined();
    });

    it('should verify value (Comparable) is correctly assigned', () => {
        // When
        const p = Equal.of(c1);

        // Then
        expect(p.comparable).toBe(c1);
    });

    describe('Statics::', () => {
        describe('Methods::()', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // When
                    const p = Equal.of(c1);

                    // Then
                    expect(p).toBeDefined();
                    expect(p).toBeInstanceOf(Equal);
                });
            });
        });
    });

    describe('Methods::()', () => {
        describe('|evaluate|', () => {
            it('should verify will return true if both comparables have same values, otherwise false', () => {
                // Given
                const p = Equal.of(c1);

                // When
                const r1 = p.evaluate(c2);
                const r2 = p.evaluate(c3);
                const r3 = p.evaluate(c1);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
                expect(r3).toBeTrue();
            });
        });
    });
});
