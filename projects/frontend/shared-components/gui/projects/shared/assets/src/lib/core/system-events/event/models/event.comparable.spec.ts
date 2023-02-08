

import { Comparable } from '../../../../common/interfaces';

import { SystemEventComparable } from './event.comparable';

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

describe('SystemEventComparable', () => {
    it('should verify instance is created', () => {
        // Given
        const eventId = 'Super Collider';
        const payload = {};

        // When
        const instance = new SystemEventComparable({ eventId, payload });

        // Then
        expect(instance).toBeDefined();
    });

    it('should verify value is correctly assigned', () => {
        // Given
        const eventId = 'Super Collider';
        const payload = {};
        const value = { eventId, payload };

        // When
        const instance = new SystemEventComparable(value);

        // Then
        expect(instance.value).toBe(value);
    });

    describe('Statics::', () => {
        describe('Methods::()', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // Given
                    const eventId = 'Super Collider';
                    const payload = {};
                    const value = { eventId, payload };

                    // When
                    const instance = SystemEventComparable.of(value);

                    // Then
                    expect(instance).toBeDefined();
                    expect(instance).toBeInstanceOf(SystemEventComparable);
                });
            });
        });
    });

    describe('Methods::()', () => {
        let v1: { eventId: string; payload: unknown };
        let v2: { eventId: string; payload: unknown };
        let v3: { eventId: string; payload: unknown };
        let v4: { eventId: string; payload: unknown };

        let c1: SystemEventComparable;
        let c2: SystemEventComparable;
        let c3: SystemEventComparable;
        let c4: SystemEventComparable;

        beforeEach(() => {
            v1 = { eventId: 'Taurus', payload: { t: 10 } };
            v2 = { eventId: 'Super Collider', payload: { t: 100 } };
            v3 = { eventId: 'Test', payload: { t: 30 } };
            v4 = { eventId: 'Taurus', payload: { t: 10 } };

            c1 = SystemEventComparable.of(v1);
            c2 = SystemEventComparable.of(v2);
            c3 = SystemEventComparable.of(v3);
            c4 = SystemEventComparable.of(v4);
        });

        describe('|compare|', () => {
            it('should verify will return 0 for equal', () => {
                // When
                const comparison = c1.compare(c4);

                // Then
                expect(comparison).toEqual(0);
            });

            it('should verify will return -1 for greaterThan', () => {
                // When
                const comparison = c2.compare(c1);

                // Then
                expect(comparison).toEqual(-1);
            });

            it('should verify will return -1 for lessThan', () => {
                // When
                const comparison = c2.compare(c3);

                // Then
                expect(comparison).toEqual(-1);
            });

            it('should verify will return -1 given comparable is not instance of the current Constructor', () => {
                // Given
                const c10 = new ComparableStub(v2);

                // When
                const comparison = c1.compare(c10);

                // Then
                expect(comparison).toEqual(-1);
            });
        });
    });
});
