/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../utils';

import { Comparable, ComparableImpl } from '../../../common';

import { AbstractComponentModel } from './component.model.interface';

export class ComponentModelComparable extends ComparableImpl<AbstractComponentModel> {
    /**
     * ** Constructor.
     */
    constructor(model: AbstractComponentModel) {
        super(model);
    }

    /**
     * ** Factory method.
     */
    static override of(model: AbstractComponentModel): ComponentModelComparable {
        return new ComponentModelComparable(model);
    }

    /**
     * @inheritDoc
     */
    override compare(comparable: Comparable): number {
        if (comparable instanceof ComponentModelComparable) {
            return this._compareEquality(comparable);
        } else {
            return -1;
        }
    }

    private _compareEquality(comparable: ComponentModelComparable): number {
        if (!(this.value instanceof AbstractComponentModel)) {
            return -1;
        }

        if (!(comparable.value instanceof AbstractComponentModel)) {
            return -1;
        }

        if (this.value === comparable.value) {
            return 0;
        }

        if (this.value.status !== comparable.value.status) {
            return -1;
        }

        if (this.value.getTask() !== comparable.value.getTask()) {
            return -1;
        }

        if (!this.value.getComponentState().errors.equals(comparable.value.getComponentState().errors)) {
            return -1;
        }

        if (this.value.getComponentState().data === comparable.value.getComponentState().data) {
            return 0;
        }

        if (CollectionsUtil.areMapsEqual(this.value.getComponentState().data, comparable.value.getComponentState().data)) {
            return 0;
        }

        return -1;
    }
}
