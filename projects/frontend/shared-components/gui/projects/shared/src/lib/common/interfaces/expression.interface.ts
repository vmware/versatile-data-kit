

import { Comparable } from './comparable.interface';
import { Predicate } from './predicate.interface';

/**
 * ** Interface for Expression.
 *
 * @author gorankokin
 */
export interface Expression<T extends Predicate = Predicate> {
    /**
     * ** Predicates Array.
     */
    readonly predicates: T[];

    /**
     * ** Evaluate Expression to boolean (true or false).
     */
    evaluate(comparable?: Comparable): boolean;
}
