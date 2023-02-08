

import { Comparable } from '../../interfaces';

import { ComparableImpl } from './comparable.impl';

class ComparableStub implements Comparable {
    public readonly value: unknown;

    constructor(value: unknown) {
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

describe('ComparableImpl', () => {
    it('should verify instance is created', () => {
        // Given
        const value = 'Super Collider';

        // When
        const instance = new ComparableImpl(value);

        // Then
        expect(instance).toBeDefined();
    });

    it('should verify value is correctly assigned', () => {
        // Given
        const value = 'Super Collider';

        // When
        const instance = new ComparableImpl(value);

        // Then
        expect(instance.value).toBe(value);
    });

    describe('Statics::', () => {
        describe('Methods::()', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // Given
                    const value = 'Super Collider';

                    // When
                    const instance = ComparableImpl.of(value);

                    // Then
                    expect(instance).toBeDefined();
                    expect(instance).toBeInstanceOf(ComparableImpl);
                });
            });
        });
    });

    describe('Methods::()', () => {
        let v1: unknown;
        let v2: unknown;
        let v3: unknown;
        let v4: unknown;
        let v5: unknown;
        let v6: unknown;
        let v7: unknown;
        let v8: unknown;

        let c1: ComparableImpl;
        let c2: ComparableImpl;
        let c3: ComparableImpl;
        let c4: ComparableImpl;
        let c5: ComparableImpl;
        let c6: ComparableImpl;
        let c7: ComparableImpl;
        let c8: ComparableImpl;

        beforeEach(() => {
            v1 = null;
            v2 = undefined;
            v3 = 'Super Collider';
            v4 = 10;
            v5 = 'Super Collider';
            v6 = 11;
            v7 = 10;
            v8 = 'Taurus';

            c1 = ComparableImpl.of(v1);
            c2 = ComparableImpl.of(v2);
            c3 = ComparableImpl.of(v3);
            c4 = ComparableImpl.of(v4);
            c5 = ComparableImpl.of(v5);
            c6 = ComparableImpl.of(v6);
            c7 = ComparableImpl.of(v7);
            c8 = ComparableImpl.of(v8);
        });

        describe('|compare|', () => {
            it('should verify will return 0 for equal', () => {
                // When
                const comparison = c3.compare(c5);

                // Then
                expect(comparison).toEqual(0);
            });

            it('should verify will return 1 for greaterThan', () => {
                // When
                const comparison = c8.compare(c5);

                // Then
                expect(comparison).toEqual(1);
            });

            it('should verify will return -1 for lessThan', () => {
                // When
                const comparison = c5.compare(c8);

                // Then
                expect(comparison).toEqual(-1);
            });

            it('should verify will return -1 given comparable is not instance of the current Constructor', () => {
                // Given
                const c10 = new ComparableStub(v2);

                // When
                const comparison = c5.compare(c10);

                // Then
                expect(comparison).toEqual(-1);
            });
        });

        describe('|isNil|', () => {
            it('should verify will return true if value is null or undefined, otherwise false', () => {
                // When
                const r1 = c1.isNil();
                const r2 = c2.isNil();
                const r3 = c3.isNil();
                const r4 = c4.isNil();

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeTrue();
                expect(r3).toBeFalse();
                expect(r4).toBeFalse();
            });
        });

        describe('|notNil|', () => {
            it('should verify will return false if value is null or undefined, otherwise true', () => {
                // When
                const r1 = c1.notNil();
                const r2 = c2.notNil();
                const r3 = c3.notNil();
                const r4 = c4.notNil();

                // Then
                expect(r1).toBeFalse();
                expect(r2).toBeFalse();
                expect(r3).toBeTrue();
                expect(r4).toBeTrue();
            });
        });

        describe('|like|', () => {
            it('should verify will return true if values are similar, otherwise false', () => {
                // When
                const r1 = c3.like(c5);
                const r2 = c3.like(c8);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
            });
        });

        describe('|equal|', () => {
            it('should verify will return true if values are equal, otherwise false', () => {
                // When
                const r1 = c3.equal(c5);
                const r2 = c3.equal(c8);
                const r3 = c4.equal(c7);
                const r4 = c4.equal(c6);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
                expect(r3).toBeTrue();
                expect(r4).toBeFalse();
            });
        });

        describe('|notEqual|', () => {
            it('should verify will return true if values are not equal, otherwise false', () => {
                // When
                const r1 = c3.notEqual(c5);
                const r2 = c3.notEqual(c8);
                const r3 = c4.notEqual(c7);
                const r4 = c4.notEqual(c6);

                // Then
                expect(r1).toBeFalse();
                expect(r2).toBeTrue();
                expect(r3).toBeFalse();
                expect(r4).toBeTrue();
            });
        });

        describe('|lessThan|', () => {
            it('should verify will return true if value is less than provided, otherwise false', () => {
                // When
                const r1 = c4.lessThan(c6);
                const r2 = c6.lessThan(c4);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
            });
        });

        describe('|lessThanInclusive|', () => {
            it('should verify will return true if value is less than or equal to provided, otherwise false', () => {
                // When
                const r1 = c4.lessThanInclusive(c6);
                const r2 = c6.lessThanInclusive(c4);
                const r3 = c4.lessThanInclusive(c7);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
                expect(r3).toBeTrue();
            });
        });

        describe('|greaterThan|', () => {
            it('should verify will return true if value is greater than provided, otherwise false', () => {
                // When
                const r1 = c6.greaterThan(c4);
                const r2 = c4.greaterThan(c6);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
            });
        });

        describe('|greaterThanInclusive|', () => {
            it('should verify will return true if value is greater than or equal to provided, otherwise false', () => {
                // When
                const r1 = c6.greaterThanInclusive(c4);
                const r2 = c4.greaterThanInclusive(c6);
                const r3 = c7.greaterThanInclusive(c4);

                // Then
                expect(r1).toBeTrue();
                expect(r2).toBeFalse();
                expect(r3).toBeTrue();
            });
        });
    });
});
