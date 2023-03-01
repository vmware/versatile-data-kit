/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ConfirmationModalOptions } from '../../model/modal-options';
import { ModalComponentDirective } from '../modal/modal.component';

@Component({
    selector: 'lib-confirmation-dialog-modal',
    templateUrl: './confirmation-dialog-modal.component.html',
    styleUrls: ['./confirmation-dialog-modal.component.scss'],
})
export class ConfirmationDialogModalComponent extends ModalComponentDirective {
    @Input() confirmationInput: string;
    @Output() changeStatus: EventEmitter<string> = new EventEmitter<string>();

    constructor() {
        super();
        this.options = new ConfirmationModalOptions();
    }

    override confirm(): void {
        super.confirm();

        this.changeStatus.emit();
    }
}
