/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ElementRef, Injectable, OnDestroy, Renderer2 } from '@angular/core';

import { CollectionsUtil } from '../../../utils';

import { ApiErrorMessage, ErrorRecord, TaurusObject } from '../../../common';

import { getApiFormattedErrorMessage } from '../../../core';

@Injectable()
export class PlaceholderService extends TaurusObject implements OnDestroy {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'PlaceholderService';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Placeholder-Service';

    // lookup flags
    private _lookupInProgress = false;
    private _isGridParentFound = false;
    private _finderLookupTimeoutRef: number;

    // styling elements
    private _headElement: HTMLHeadElement;
    private _gridStyleElement: HTMLStyleElement;
    private _standalonePlaceholderStyleElement: HTMLElement;

    // utility
    private readonly _gridRandomAttribute: string;
    private readonly _standalonePlaceholderRandomAttribute: string;

    // temporary storage
    private _elementRef: ElementRef<HTMLElement>;
    private _hideDefaultEmptyStateImageInGrid = false;

    /**
     * ** Constructor.
     */
    constructor(private readonly renderer2: Renderer2) {
        super(PlaceholderService.CLASS_NAME);

        this._gridRandomAttribute = CollectionsUtil.generateRandomString();
        this._standalonePlaceholderRandomAttribute = CollectionsUtil.generateRandomString();
    }

    /**
     * ** Extract public name of classes from multiple error records.
     */
    static extractClassesPublicNames(errorRecords: ErrorRecord[]): string {
        const publicNames = errorRecords
            .map((r) => PlaceholderService.extractClassPublicName(r))
            .filter((publicName) => CollectionsUtil.isString(publicName) && publicName.length > 0);

        return CollectionsUtil.uniqueArray(publicNames).join(', ');
    }

    /**
     * ** Extract class public name from provided error record.
     */
    static extractClassPublicName(errorRecord: ErrorRecord): string {
        if (errorRecord) {
            if (errorRecord.code && errorRecord.code.length > 0) {
                /**
                 * class public name is second with underscore following pattern described in {@link ErrorRecord.code}
                 */
                const codeChunks = errorRecord.code.split('_');

                if (codeChunks.length >= 3) {
                    const publicName = codeChunks[1];

                    if (publicName && publicName.length > 2) {
                        const publicNameNormalized = publicName.replace(/-/g, ' ');

                        return publicNameNormalized.substring(0, 1).toUpperCase() + publicNameNormalized.substring(1).toLowerCase();
                    }
                }
            }
        }

        return '';
    }

    /**
     * ** Refines elements state and their corresponding styles.
     */
    refineElementsState(elementRef: ElementRef<HTMLElement>, hideDefaultEmptyStateImageInGrid: boolean): void {
        if (CollectionsUtil.isDefined(elementRef)) {
            this._elementRef = elementRef;
        }

        if (CollectionsUtil.isDefined(hideDefaultEmptyStateImageInGrid)) {
            this._hideDefaultEmptyStateImageInGrid = hideDefaultEmptyStateImageInGrid;
        }

        if (this._lookupInProgress) {
            return;
        }

        if (!this._isGridParentFound) {
            this._lookupInProgress = true;

            this._findHeadElement();

            this._findPlaceholderParentGrid()
                .then((placeholderGridParent) => {
                    this._isGridParentFound = !!placeholderGridParent;

                    this._removeStandalonePlaceholderStyle();

                    this._appendGridPlaceholderStyle();
                    this._addGridDataAttribute(placeholderGridParent);
                    this._toggleGridPlaceholderStyle();
                })
                .catch((_error) => {
                    this._isGridParentFound = false;

                    this._removeGridPlaceholderStyle();

                    this._appendStandalonePlaceholderStyle();
                    this._addStandalonePlaceholderDataAttribute();
                    this._toggleStandalonePlaceholderStyle();
                })
                .finally(() => {
                    this._lookupInProgress = false;
                });
        } else {
            this._toggleGridPlaceholderStyle();
            this._toggleStandalonePlaceholderStyle();
        }
    }

    /**
     * ** Get API formatted error message from provided Error.
     */
    extractErrorInformation(error: Error): ApiErrorMessage {
        return getApiFormattedErrorMessage(error);
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy(): void {
        if (this._finderLookupTimeoutRef) {
            window.clearTimeout(this._finderLookupTimeoutRef);
        }

        this._removeGridPlaceholderStyle();
        this._removeStandalonePlaceholderStyle();

        super.ngOnDestroy();
    }

    private _findPlaceholderParentGrid(): Promise<HTMLElement> {
        let parentElementFinderAttempts = 0;

        let resolveRef: (value: HTMLElement) => void;
        let rejectRef: (reason: string) => void;

        const parentFinder = () => {
            parentElementFinderAttempts++;

            const firstLevelParent: HTMLElement = this.renderer2.parentNode(this._elementRef.nativeElement) as HTMLElement;
            if (firstLevelParent) {
                const foundParentGrid = this._traverseToFindParentGrid(firstLevelParent);

                if (foundParentGrid) {
                    resolveRef(foundParentGrid);
                } else {
                    rejectRef('Cannot find parent grid (clr-datagrid)!');
                }
            } else if (parentElementFinderAttempts < 200) {
                this._finderLookupTimeoutRef = window.setTimeout(() => {
                    this._finderLookupTimeoutRef = null;

                    parentFinder();
                }, 25);
            } else {
                rejectRef('Cannot find parent grid (clr-datagrid)!');
            }
        };

        return new Promise((resolve, reject) => {
            resolveRef = resolve;
            rejectRef = reject;

            parentFinder();
        });
    }

    private _traverseToFindParentGrid(element: HTMLElement): HTMLElement {
        let loop = 0;
        let parentElement: HTMLElement = element;

        while (loop < 15) {
            if (parentElement) {
                loop++;

                if (!parentElement.tagName) {
                    break;
                }

                if (parentElement.tagName.toLowerCase() === 'clr-datagrid') {
                    return parentElement;
                }

                parentElement = this.renderer2.parentNode(parentElement) as HTMLElement;
            } else {
                break;
            }
        }

        return null;
    }

    private _findHeadElement(): void {
        if (this._headElement) {
            return;
        }

        this._headElement = document.querySelector('head');
    }

    private _appendGridPlaceholderStyle(): void {
        if (!this._gridStyleElement) {
            this._gridStyleElement = this.renderer2.createElement('style') as HTMLStyleElement;

            this.renderer2.setAttribute(this._gridStyleElement, 'data-shared-grid-style', this._gridRandomAttribute);
            this.renderer2.appendChild(this._headElement, this._gridStyleElement);
        }
    }

    private _appendStandalonePlaceholderStyle(): void {
        if (!this._standalonePlaceholderStyleElement) {
            this._standalonePlaceholderStyleElement = this.renderer2.createElement('style') as HTMLStyleElement;

            this.renderer2.setAttribute(
                this._standalonePlaceholderStyleElement,
                'data-shared-placeholder-style',
                this._standalonePlaceholderRandomAttribute
            );
            this.renderer2.appendChild(this._headElement, this._standalonePlaceholderStyleElement);
        }
    }

    private _addGridDataAttribute(element: HTMLElement): void {
        if (!element) {
            return;
        }

        this.renderer2.setAttribute(element, 'data-shared-grid', this._gridRandomAttribute);
    }

    private _addStandalonePlaceholderDataAttribute(): void {
        if (!this._elementRef.nativeElement) {
            return;
        }

        this.renderer2.setAttribute(this._elementRef.nativeElement, 'data-shared-placeholder', this._standalonePlaceholderRandomAttribute);
    }

    private _toggleGridPlaceholderStyle(): void {
        if (!this._gridStyleElement) {
            return;
        }

        this._gridStyleElement.innerHTML = `
            clr-datagrid[data-shared-grid="${this._gridRandomAttribute}"] clr-dg-placeholder .datagrid-placeholder.datagrid-empty {
                justify-content: center;
            }
            clr-datagrid[data-shared-grid="${this._gridRandomAttribute}"] clr-dg-placeholder .datagrid-placeholder-image {
                display: ${this._hideDefaultEmptyStateImageInGrid ? 'none' : 'block'};
            }
        `;
    }

    private _toggleStandalonePlaceholderStyle(): void {
        if (!this._standalonePlaceholderStyleElement) {
            return;
        }

        this._standalonePlaceholderStyleElement.innerHTML = `
            shared-placeholder[data-shared-placeholder="${this._standalonePlaceholderRandomAttribute}"] {
                margin-top: 5rem;
            }
        `;
    }

    private _removeGridPlaceholderStyle(): void {
        if (this._gridStyleElement) {
            this.renderer2.removeChild(this._headElement, this._gridStyleElement);
        }
    }

    private _removeStandalonePlaceholderStyle(): void {
        if (this._standalonePlaceholderStyleElement) {
            this.renderer2.removeChild(this._headElement, this._standalonePlaceholderStyleElement);
        }
    }
}
