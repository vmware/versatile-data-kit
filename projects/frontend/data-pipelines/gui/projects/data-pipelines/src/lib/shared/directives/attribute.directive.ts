/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, ElementRef, Input, OnChanges, OnInit, Renderer2, SimpleChanges } from '@angular/core';

import { CollectionsUtil, PrimitivesNil, TaurusObject } from '@versatiledatakit/shared';

export interface Attributes {
    [attribute: string]: PrimitivesNil;
}

/**
 * ** Directive that set provided object as Element attributes.
 *
 * @author gorankokin
 */
@Directive({
    selector: '[libSetAttributes]'
})
export class AttributesDirective extends TaurusObject implements OnInit, OnChanges {
    /**
     * ** Input attributes that should be applied to host element.
     */
    @Input() attributes: Attributes;

    private _attributesCopy: Attributes;

    /**
     * ** Constructor.
     */
    constructor(
        private readonly el: ElementRef,
        private readonly renderer: Renderer2
    ) {
        super();
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(_changes: SimpleChanges) {
        this._transformAttributes();
    }

    /**
     * @inheritDoc
     */
    ngOnInit() {
        this._transformAttributes();
    }

    private _transformAttributes(): void {
        if (CollectionsUtil.isEqual(this.attributes, this._attributesCopy)) {
            return;
        }

        if (CollectionsUtil.isNil(this.attributes)) {
            if (CollectionsUtil.isNil(this._attributesCopy)) {
                return;
            }

            CollectionsUtil.iterateObject(this._attributesCopy, (_attributeValue, attributeName) => {
                this._removeAttribute(attributeName);
            });

            return;
        }

        if (!CollectionsUtil.isLiteralObject(this.attributes)) {
            return;
        }

        this._attributesCopy = CollectionsUtil.cloneDeep(this.attributes);

        CollectionsUtil.iterateObject(this._attributesCopy, (attributeValue, attributeName) => {
            this._setOrRemoveAttribute(attributeName, attributeValue);
        });
    }

    private _setOrRemoveAttribute(attributeName: string, attributeValue: unknown): void {
        if (AttributesDirective._isTruthy(attributeValue)) {
            this._setAttribute(attributeName, attributeValue);
        } else {
            this._removeAttribute(attributeName);
        }
    }

    private _setAttribute(attributeName: string, attributeValue: unknown): void {
        this.renderer.setAttribute(this.el.nativeElement, attributeName, attributeValue as string);
    }

    private _removeAttribute(attributeName: string): void {
        this.renderer.removeAttribute(this.el.nativeElement, attributeName);
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering,@typescript-eslint/no-explicit-any
    private static _isTruthy(value: any): boolean {
        return AttributesDirective._valueNotIn(value, [undefined, false, null, 'delete', 'false', '']);
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering,@typescript-eslint/no-explicit-any
    private static _valueNotIn(value: any, forbiddenValues: any[]): boolean {
        return forbiddenValues.every((prop) => value !== prop);
    }
}
