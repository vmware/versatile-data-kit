/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { VdkFormSectionContainerComponent } from './form-section-container.component';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { Component, DebugElement, ViewChild } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';

import { ClarityModule } from '@clr/angular';

import { FORM_STATE, VdkFormState } from './form-section-container.component';
import { VdkFormSectionComponent } from '../form-section';
import { VdkSimpleTranslateModule, VdkSimpleTranslateService } from '../../ngx-utils';

let fixture: ComponentFixture<TestHostComponent>;
let hostComp: TestHostComponent;
let page: PageObject;
let el: Element;

class PageObject {
    fixtureElement: DebugElement;

    constructor() {}

    populateLocators(): void {
        this.fixtureElement = fixture.debugElement.query(By.css('vdk-form-section-container'));
    }

    getReadOnlySectionElements(): NodeListOf<Element> {
        return el.querySelectorAll('.form-section-readonly');
    }

    getEditSectionElements(): NodeListOf<Element> {
        return el.querySelectorAll('.form-section-edit');
    }

    setInputValue(inputName: string, inputValue: any) {
        hostComp.editProfileForm.controls[inputName].setValue(inputValue);
        hostComp.editProfileForm.controls[inputName].markAsDirty();
    }

    getSaveBtnSpan(): HTMLElement | undefined {
        const span = fixture.debugElement.queryAll(By.css('.csp-save-button span'));
        if (span && span.length > 0) {
            return span[0].nativeElement;
        }
        return undefined;
    }
}

@Component({
    template: ` <form [formGroup]="editProfileForm" (ngSubmit)="doSubmit(editProfileForm.value)">
        <vdk-form-section-container [isSubmitEnabled]="false" [formState]="formState" (sectionState)="sectionState($event)">
            <div class="section-title">Title</div>

            <div class="form-section-readonly">
                <div class="form-group row">
                    <div>
                        <label>Name</label>
                    </div>
                    <div>
                        <span data-test-id="first-name">firstName</span>
                    </div>
                </div>
            </div>

            <div class="form-section-edit">
                <div class="form-group row">
                    <div>
                        <label class="required" for="firstNameInput">First Name</label>
                    </div>
                    <div>
                        <label for="firstNameInput">
                            <input type="text" class="form-control" id="firstNameInput" formControlName="firstName" />
                        </label>
                    </div>
                </div>
            </div>
        </vdk-form-section-container>
    </form>`
})
class TestHostComponent {
    @ViewChild(VdkFormSectionContainerComponent, { static: false })
    child: VdkFormSectionContainerComponent;
    formState: VdkFormState;

    editProfileForm = new FormGroup({
        firstName: new FormControl()
    });
}

describe('Form Section Container Component', () => {
    function createComponent() {
        fixture = TestBed.createComponent(TestHostComponent);
        hostComp = fixture.componentInstance;
        el = fixture.nativeElement;
        fixture.detectChanges();
        page = new PageObject();
        page.populateLocators();
    }

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [ReactiveFormsModule, VdkSimpleTranslateModule, BrowserAnimationsModule, ClarityModule],
            providers: [VdkSimpleTranslateService, FormBuilder],
            declarations: [TestHostComponent, VdkFormSectionComponent, VdkFormSectionContainerComponent]
        });

        createComponent();
        fixture.detectChanges();
    }));

    it('should project .title content correctly', () => {
        expect(el.querySelector('.section-title').textContent).toContain('Title');
    });

    it('should readOnly and Edit sections to be toggled on Edit', () => {
        expect(page.getReadOnlySectionElements().length).toBe(1, 'Readonly Section shown initially');
        expect(page.getEditSectionElements().length).toBe(0, 'Edit section hidden initially');
        expect(el.querySelectorAll('.csp-edit-button').length).toBe(1, 'Edit button shown initially');
        const editButton: HTMLInputElement = <HTMLInputElement>el.querySelector('.csp-edit-button');
        editButton.click();
        fixture.detectChanges();

        expect(page.getReadOnlySectionElements().length).toBe(0, 'Readonly section hidden on Edit button');
        expect(page.getEditSectionElements().length).toBe(1, 'Edit section shown on Edit button');
    });

    it('should readOnly and Edit sections to be toggled on Cancel', () => {
        const editButton: HTMLInputElement = <HTMLInputElement>el.querySelector('.csp-edit-button');
        editButton.click();
        fixture.detectChanges();

        expect(el.querySelectorAll('.csp-cancel-button').length).toBe(1, 'Cancel button to be shown');
        const cancelButton: HTMLInputElement = <HTMLInputElement>el.querySelector('.csp-cancel-button');
        cancelButton.click();
        fixture.detectChanges();

        expect(page.getReadOnlySectionElements().length).toBe(1, 'Readonly section shown on Cancel');
        expect(page.getEditSectionElements().length).toBe(0, 'Edit section hidden on Cancel');
    });

    it('should show Readonly and Edit section after save', () => {
        const editButton: HTMLInputElement = <HTMLInputElement>el.querySelector('.csp-edit-button');
        editButton.click();
        fixture.detectChanges();

        page.setInputValue('firstName', 'firstName');
        expect(el.querySelectorAll('.csp-save-button').length).toBe(1, 'Save button shown');
        const saveButton: HTMLInputElement = <HTMLInputElement>el.querySelector('.csp-save-button');
        expect(page.getSaveBtnSpan().innerText.trim()).toBe('Save', 'save btn shown');
        saveButton.click();
        fixture.detectChanges();

        expect(saveButton.disabled).toEqual(true, 'Save to be disabled');
        hostComp.formState = new VdkFormState(FORM_STATE.CAN_EDIT);
        fixture.detectChanges();

        expect(page.getReadOnlySectionElements().length).toBe(1, 'Readonly Section shown');
        expect(page.getEditSectionElements().length).toBe(0, 'Edit Section hidden');
    });
});
