/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Criteria } from '../../interfaces';

/**
 * ** And criteria that filters elements in Array and remove those that does not meet all criterias.
 */
export class AndCriteria<T> implements Criteria<T> {
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
        let elementsMeetCriteria: T[] = [...elements];

        for (const criteria of this.criterias) {
            elementsMeetCriteria = criteria.meetCriteria(elementsMeetCriteria);

            if (elementsMeetCriteria.length === 0) {
                break;
            }
        }

        return elementsMeetCriteria;
    }
}
