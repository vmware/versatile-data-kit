/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Output } from '@angular/core';

import { DeleteModalOptions } from '../../model';

import { ModalComponentDirective } from '../modal';

@Component({
    selector: 'lib-delete-modal',
    templateUrl: './delete-modal.component.html',
    styleUrls: ['./delete-modal.component.css']
})
export class DeleteModalComponent extends ModalComponentDirective {
    @Output() delete: EventEmitter<undefined> = new EventEmitter<undefined>();

    constructor() {
        super();
        this.options = new DeleteModalOptions();
    }

    /**
     * emit that the user confirmed that it want to delete the item
     * and close the modal
     */
    override confirm(): void {
        super.confirm();

        this.delete.emit();
    }
}
