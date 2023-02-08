

import { Comparable } from './comparable.interface';

/**
 * ** Interface for Predicate Classes.
 *
 * @author gorankokin
 */
export interface Predicate<T extends Comparable = Comparable, C extends Comparable = T> {
    /**
     * ** Stored comparable that have to be compared with provided comparable.
     */
    readonly comparable: T;

    /**
     * ** Evaluate Predicate to boolean (true or false).
     */
    evaluate(comparable: C): boolean;
}
