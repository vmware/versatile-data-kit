/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Criteria } from '../../interfaces';

/**
 * ** Or criteria that filters elements in Array and remove those that does not meet at least one criterias.
 */
export class OrCriteria<T> implements Criteria<T> {
    /**
     * @inheritDoc
     */
    readonly criterias: Criteria<T>[];

    /**
     * ** Constructor.
     */
    constructor(...criterias: Criteria<T>[]) {
        this.criterias = criterias;
    }

    /**
     * @inheritDoc
     */
    meetCriteria(elements: T[]): T[] {
        return this.criterias.reduce((elementsMeetCriteria, criteria) => {
            const singleCriteriaMetElements = criteria.meetCriteria(elements);

            for (const element of singleCriteriaMetElements) {
                if (!elementsMeetCriteria.includes(element)) {
                    elementsMeetCriteria.push(element);
                }
            }

            return elementsMeetCriteria;
        }, [] as T[]);
    }
}
