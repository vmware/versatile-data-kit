/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { ElementRef, HostBinding, Output, EventEmitter, Component, OnInit, Input, ViewChild } from '@angular/core';
import { VdkSimpleTranslateService } from '../../ngx-utils';

import { TRANSLATIONS } from './copy-to-clipboard-button.l10n';

const SHOW_CHECKBOX_TIMEOUT = 1500;

@Component({
    selector: 'vdk-copy-to-clipboard-button',
    templateUrl: './copy-to-clipboard-button.component.html',
    styleUrls: ['./copy-to-clipboard-button.component.scss']
})
export class VdkCopyToClipboardButtonComponent implements OnInit {
    @ViewChild('area', { read: ElementRef, static: false }) area: ElementRef;

    @HostBinding('class') @Input('class') classList: string = '';

    @Input() value: string;
    @Input() ariaLabel: string = '';
    @Input() copyAlert: string;
    @Input() size = 16;
    @Input() tooltip = '';
    @Input() btnLabel = ''; // if no label specified, show the normal copy icon
    @Input() btnClasses = ['btn-outline']; // if no label specified, show the normal copy icon
    @Input() disabled: boolean = false;
    @Input() tooltipDirection = 'top-left';

    @Output() copyClick = new EventEmitter<null>();

    private firstLoad = true; // show correct icon first

    btnClassesToApply: string;
    bounds: string;
    hasProjectedContent: boolean = false;
    isSafari: boolean = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    copied: boolean = false;

    constructor(private el: ElementRef, public translateService: VdkSimpleTranslateService) {
        this.translateService.loadTranslationsForComponent('copy-to-clipboard-button', TRANSLATIONS);
    }

    ngOnInit() {
        this.bounds = this.size + 6 + 'px';

        this.hasProjectedContent = this.el.nativeElement.innerText.trim();

        this.calculateClassesToApply();
        this.copyAlert = this.copyAlert || this.translateService.translate('copy-to-clipboard-button.copied');
    }

    calculateClassesToApply() {
        let classes: Array<string> = [];

        if (!this.btnLabel.length) {
            classes.push('icon-btn');
        }

        if (this.btnLabel.length) {
            classes = classes.concat(this.btnClasses);
        }

        if (this.disabled) {
            classes.push('disabled');
        }

        this.btnClassesToApply = classes.join(' ') + ' ' + this.classList;
    }

    ngOnChanges() {
        this.calculateClassesToApply();
    }

    copyToClipboard(val: string) {
        let myWindow: any = window;

        let onCopy = (e: ClipboardEvent) => {
            e.preventDefault();

            if (e.clipboardData) {
                e.clipboardData.setData('text/plain', val);
            } else if (myWindow.clipboardData) {
                myWindow.clipboardData.setData('Text', val);
            }

            myWindow.removeEventListener('copy', onCopy);
        };

        if (this.isSafari) {
            this.area.nativeElement.value = val;
            this.area.nativeElement.select();
            navigator.clipboard?.writeText(val);
        }

        myWindow.addEventListener('copy', onCopy);

        if (myWindow.clipboardData && myWindow.clipboardData.setData) {
            myWindow.clipboardData.setData('Text', val);
        } else {
            document.execCommand('copy');
        }
    }

    doCopy() {
        this.copyToClipboard(this.value);
        this.copyClick.emit();
        this.firstLoad = false;
        this.copied = true;
        setTimeout(() => {
            this.copied = false;
        }, SHOW_CHECKBOX_TIMEOUT);
    }
}
