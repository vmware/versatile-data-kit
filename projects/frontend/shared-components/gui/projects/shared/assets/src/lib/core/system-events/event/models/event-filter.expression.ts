

import { Comparable, Expression, Predicate } from '../../../../common';

/**
 * ** System Event Filter Expression that evaluates if some Handler should be executed or no.
 *
 * @author gorankokin
 */
export class SystemEventFilterExpression implements Expression {
    /**
     * @inheritDoc
     */
    public readonly predicates: Predicate[];

    /**
     * ** Constructor.
     */
    constructor(...predicates: Predicate[]) {
        this.predicates = predicates ?? [];
    }

    /**
     * ** Factory method.
     */
    static of(...predicates: Predicate[]): SystemEventFilterExpression {
        return new SystemEventFilterExpression(...predicates);
    }

    /**
     * ** Add Predicates to Expression.
     */
    addPredicate(...predicates: Predicate[]): void {
        this.predicates.push(...predicates);
    }

    /**
     * ** Returns value that reflects if there is any Predicate inside the Expression (SystemEventFilter).
     */
    hasPredicates(): boolean {
        return this.predicates.length > 0;
    }

    /**
     * @inheritDoc
     */
    evaluate(comparable?: Comparable): boolean {
        return this.predicates
                   .every((p) => p.evaluate(comparable));
    }
}
