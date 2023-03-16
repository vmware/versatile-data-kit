/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import {
    Component,
    Output,
    EventEmitter,
    Input,
    Host,
    Optional,
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    ViewChild,
    ElementRef
} from '@angular/core';
import { FormGroupDirective } from '@angular/forms';
import { ClrLoadingState } from '@clr/angular';

export enum FORM_STATE {
    VIEW,
    CAN_EDIT,
    EDIT,
    ERROR,
    SUBMIT
}
export class VdkFormState {
    state: FORM_STATE;

    /**
     * Optional. The section with this name identifier will be excluded from the state change.
     */
    emittingSection: string;

    /**
     * Optional.
     * All the sections in the array will change its state.
     * All the others will be excluded if this array is not empty.
     */
    sectionsToInclude: string[];

    constructor(_state: FORM_STATE, _sectionsToInclude?: string[], _emittingSection?: string) {
        this.state = _state;
        this.sectionsToInclude = _sectionsToInclude ? _sectionsToInclude : [];
        this.emittingSection = _emittingSection;
    }
}

@Component({
    selector: 'vdk-form-section-container',
    templateUrl: './form-section-container.component.html',
    styleUrls: ['form-section-container.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class VdkFormSectionContainerComponent {
    FORM_STATE = FORM_STATE; //used in the template
    _sectionState: FORM_STATE = FORM_STATE.CAN_EDIT;
    ClrLoadingState = ClrLoadingState;
    stopInitialFocus = true;

    @Input() canEditSection = true; //set to false if the section is readonly
    @Input() isSubmitEnabled: boolean; //controls the Submit(Save) button state
    @Input() sectionName: string; //unique section identifier
    @Input() editBtn = 'Edit'; //Edit button text
    @Input() cancelBtn = 'Cancel'; //Cancel button text
    @Input() saveBtn = 'Save'; //Save button text
    @Input() editBtnAriaLabel = 'Edit'; //Edit button text
    @Input() cancelBtnAriaLabel = 'Cancel'; //Cancel button text
    @Input() saveBtnAriaLabel = 'Save'; //Save button text

    @Input('formState') set formState(_formState: VdkFormState) {
        if (!_formState) {
            return;
        }

        if (
            (_formState.emittingSection && _formState.emittingSection !== this.sectionName) ||
            (!_formState.emittingSection && _formState.sectionsToInclude.length === 0) ||
            _formState.sectionsToInclude.some((name) => name === this.sectionName)
        ) {
            //on ERROR set EDIT state only on submitted section
            //to the rest of sections restore CAN_EDIT state
            if (_formState.state === FORM_STATE.ERROR) {
                if (this._sectionState === FORM_STATE.SUBMIT) {
                    this._sectionState = FORM_STATE.EDIT;
                    //put it in a microtask(make it asynchronous) to not violate detection run
                    //and avoid error for Expression changed after check
                    Promise.resolve(null).then(() => {
                        if (this.cspForm) {
                            this.cspForm.form.enable();
                        } else {
                            this.enableForm.emit();
                        }
                    });
                } else {
                    this._sectionState = FORM_STATE.CAN_EDIT;
                }
            } else {
                this.changeSectionState(_formState.state);
            }
        }
    }

    @Output() formStateChange = new EventEmitter();
    @Output() sectionStateChange = new EventEmitter();

    //Events that are used when no formGroup is found in parent component
    @Output() submitForm = new EventEmitter();
    @Output() disableForm = new EventEmitter();
    @Output() enableForm = new EventEmitter();

    @ViewChild('editButton') editButtonEl: ElementRef;

    constructor(@Optional() @Host() private cspForm: FormGroupDirective, private cdr: ChangeDetectorRef) {}

    showEditBtn() {
        return this._sectionState === FORM_STATE.CAN_EDIT && this.canEditSection;
    }

    showSaveBtn() {
        return this._sectionState === FORM_STATE.EDIT;
    }

    clickEdit() {
        this.formStateChange.emit(new VdkFormState(FORM_STATE.CAN_EDIT, [], this.sectionName));
        if (this.cspForm) {
            this.cspForm.form.enable();
        } else {
            this.enableForm.emit();
        }
        this.changeSectionState(FORM_STATE.EDIT);
    }

    clickCancel() {
        this.changeSectionState(FORM_STATE.CAN_EDIT);
    }

    // @ts-ignore
    clickSave(): boolean {
        this.formStateChange.emit(new VdkFormState(FORM_STATE.VIEW, [], this.sectionName));
        this.changeSectionState(FORM_STATE.SUBMIT);
        if (this.cspForm) {
            this.cspForm.form.disable();
            this.cspForm.onSubmit(this.cspForm.value);
            this.cspForm.form.markAsPristine();
            // cancel submitting the form since cspForm.onSubmit has been called above.
            // solves a specific issue in Firefox where onSubmit was called twice.
            return false;
        } else {
            this.disableForm.emit();
            this.submitForm.emit();
        }
    }

    changeSectionState(_sectionState: FORM_STATE) {
        if (_sectionState !== this._sectionState) {
            this.sectionStateChange.emit(new VdkFormState(_sectionState, [], this.sectionName));
            this._sectionState = _sectionState;
        }
    }

    focusEdit() {
        if (this.editButtonEl && this._sectionState === FORM_STATE.CAN_EDIT && !this.stopInitialFocus) {
            this.editButtonEl.nativeElement.focus();
        }
        if (this.stopInitialFocus) {
            this.stopInitialFocus = false;
        }
    }
}
