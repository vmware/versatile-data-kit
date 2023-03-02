/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, EventEmitter, Input, Output } from '@angular/core';

import { TaurusObject } from '@versatiledatakit/shared';

import { ModalOptions } from '../../model';

@Directive()
export abstract class ModalComponentDirective extends TaurusObject {
    @Input() options: ModalOptions;

    @Output() optionsChange: EventEmitter<ModalOptions> =
        new EventEmitter<ModalOptions>();

    @Output() cancelAction: EventEmitter<undefined> =
        new EventEmitter<undefined>();

    constructor() {
        super();
    }

    confirm() {
        this.close();
    }

    /**
     * close the modal
     */
    close(): void {
        if (!this._isNull(this.options)) {
            this.options.opened = false;
            this.optionsChange.emit(this.options);
        }
    }

    cancel() {
        this.cancelAction.emit();
        this.close();
    }

    private _isNull(value: ModalOptions): boolean {
        return value === null || value === undefined;
    }
}
