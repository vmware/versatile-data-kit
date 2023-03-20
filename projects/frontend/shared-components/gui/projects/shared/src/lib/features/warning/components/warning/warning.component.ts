/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ContentChild, HostListener, Inject, Input, OnDestroy, TemplateRef } from '@angular/core';

import { SHARED_FEATURES_CONFIG_TOKEN } from '../../../_token';

import { WarningConfig } from '../../model';

@Component({
    selector: 'shared-warning',
    templateUrl: './warning.component.html',
    styleUrls: ['./warning.component.scss']
})
export class WarningComponent implements OnDestroy {
    /**
     * ** Content projection child query for custom template with ID #customTemplate
     */
    @ContentChild('customTemplate', { read: TemplateRef }) customTemplateRef: TemplateRef<never>;

    /**
     * ** Warning text.
     */
    @Input() text = '';

    /**
     * ** Show different warning message if some resource is not found.
     */
    @Input() showNotFound = false;

    /**
     * ** Text show when flag {@link notFound} set to true.
     */
    @Input() notFoundText = '';

    /**
     * ** Size of the warning icon.
     */
    @Input() iconSize = 24;

    /**
     * ** Flag indicates if warning to be displayed as tooltip.
     *
     *      - Default is false
     */
    @Input() showTooltip = false;

    /**
     * ** Flag indicates if warning tooltip to be auto open on mouse icon hover.
     *
     *      - Works only with context with {@link showTooltip}
     *      - Default is true
     */
    @Input() tooltipHoverAutoOpen = true;

    /**
     * ** Field gives position of warning tooltip.
     *
     *      - Works only with context with {@link showTooltip}
     */
    @Input() tooltipPosition: 'top-left' | 'top-middle' | 'top-right' | 'bottom-left' | 'bottom-middle' | 'bottom-right';

    /**
     * ** Field gives size of warning tooltip.
     *
     *      - Works only with context with {@link showTooltip}
     *      - Default is 'lg'
     */
    @Input() tooltipSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' = 'lg';

    /**
     * ** Flag indicates whether to append Service desk link.
     */
    @Input() addServiceDeskLink = false;

    /**
     * ** Field provides name of the impacted services, if provided.
     *
     *      - Default is empty
     */
    @Input() impactedServices: string = null;

    @HostListener('click', ['$event'])
    onClick($event: MouseEvent): void {
        if (
            $event &&
            $event.target &&
            ($event.target as HTMLElement).tagName === 'A' &&
            ($event.target as HTMLAnchorElement).href &&
            ($event.target as HTMLAnchorElement).href.length > 0 &&
            ($event.target as HTMLAnchorElement).href.trim() !== '#'
        ) {
            // don't prevent default if click is on anchor element and has navigation url
            return;
        }

        $event.preventDefault();
        $event.stopImmediatePropagation();
    }

    @HostListener('mouseenter', ['$event'])
    mouseEnter($event: MouseEvent): void {
        if (!this.tooltipHoverAutoOpen) {
            return;
        }

        this._clearTimeout();

        $event.preventDefault();
        $event.stopImmediatePropagation();

        this.isSignpostOpen = true;
    }

    @HostListener('mouseleave', ['$event'])
    mouseLeave($event: MouseEvent): void {
        if (!this.tooltipHoverAutoOpen) {
            return;
        }

        this._clearTimeout();

        $event.preventDefault();
        $event.stopImmediatePropagation();

        this._timeoutRef = window.setTimeout(() => {
            this.isSignpostOpen = false;
        }, 150);
    }

    /**
     * ** Flag that indicates if signpost is opened or closed.
     *
     *      - TRUE - opened
     *      - FALSE - closed
     */
    isSignpostOpen = false;

    /**
     * ** Service request url to portal.
     */
    serviceRequestUrl = '#';

    private _timeoutRef: number;

    /**
     * ** Constructor.
     */
    constructor(@Inject(SHARED_FEATURES_CONFIG_TOKEN) private readonly featureConfig: WarningConfig) {
        if (featureConfig && featureConfig.warning && featureConfig.warning.serviceRequestUrl) {
            this.serviceRequestUrl = featureConfig.warning.serviceRequestUrl;
        }
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy(): void {
        this._clearTimeout();
    }

    private _clearTimeout(): void {
        if (this._timeoutRef) {
            window.clearTimeout(this._timeoutRef);
        }
    }
}
