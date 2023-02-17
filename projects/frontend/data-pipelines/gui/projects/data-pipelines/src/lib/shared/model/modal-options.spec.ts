/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { EditModalOptions, ConfirmationModalOptions, DeleteModalOptions } from './modal-options';

describe('ModalOptions', () => {

    it('DeleteModalOptions have initial values', () => {
        const deleteModalOptions = new DeleteModalOptions();
        expect(deleteModalOptions.opened).toBeFalse();
        expect(deleteModalOptions.title).toBeDefined();
        expect(deleteModalOptions.message).toBeDefined();
        expect(deleteModalOptions.cancelBtn).toBeDefined();
        expect(deleteModalOptions.showCancelBtn).toBeTrue();
        expect(deleteModalOptions.okBtn).toBeDefined();
        expect(deleteModalOptions.showOkBtn).toBeTrue();
        expect(deleteModalOptions.showCloseX).toBeTrue();
    });

    it('EditModalOptions have initial values', () => {
        const editModalOptions = new EditModalOptions();
        expect(editModalOptions.opened).toBeFalse();
        expect(editModalOptions.title).toBeDefined();
        expect(editModalOptions.message).toBeDefined();
        expect(editModalOptions.cancelBtn).toBeDefined();
        expect(editModalOptions.showCancelBtn).toBeTrue();
        expect(editModalOptions.okBtn).toBeDefined();
        expect(editModalOptions.showOkBtn).toBeTrue();
        expect(editModalOptions.showCloseX).toBeTrue();
    });

    it('ConfirmationModalOptions have initial values', () => {
        const confirmationModalOptions = new ConfirmationModalOptions();
        expect(confirmationModalOptions.opened).toBeFalse();
        expect(confirmationModalOptions.title).toBeDefined();
        expect(confirmationModalOptions.message).toBeDefined();
        expect(confirmationModalOptions.cancelBtn).toBeDefined();
        expect(confirmationModalOptions.showCancelBtn).toBeTrue();
        expect(confirmationModalOptions.okBtn).toBeDefined();
        expect(confirmationModalOptions.showOkBtn).toBeTrue();
        expect(confirmationModalOptions.showCloseX).toBeTrue();
    });

});
