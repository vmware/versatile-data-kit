/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { Component, ViewChild } from '@angular/core';

import { ClarityModule } from '@clr/angular';

import { VdkFormSectionComponent } from './form-section.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@Component({
    template: `
        <vdk-form-section [focused]="focused">
            <span class="form-section-header">Test header</span>
            <span class="form-section-content">Test content</span>
            <span class="form-section-footer">Test footer</span>
        </vdk-form-section>
    `
})
class TestHostComponent {
    @ViewChild(VdkFormSectionComponent, { static: true })
    child: VdkFormSectionComponent;
    focused: boolean = false;
}

describe('VdkFormSectionComponent', () => {
    let fixture: ComponentFixture<TestHostComponent>;
    let comp: VdkFormSectionComponent;
    let el: any;

    function createComponent() {
        fixture = TestBed.createComponent(TestHostComponent);
        comp = fixture.componentInstance.child;
        el = fixture.debugElement.nativeElement;
        fixture.detectChanges();
    }

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            imports: [BrowserAnimationsModule, ClarityModule],
            providers: [],
            declarations: [TestHostComponent, VdkFormSectionComponent]
        });

        createComponent();
        fixture.detectChanges();
    }));

    it('should project .form-section-header content correctly', () => {
        const headers: NodeListOf<Element> = el.querySelectorAll('vdk-form-section span.form-section-header');
        expect(headers.length).toBe(1);
    });

    it('should project .form-section-content content correctly', () => {
        const content: NodeListOf<Element> = el.querySelectorAll('vdk-form-section span.form-section-content');
        expect(content.length).toBe(1);
    });

    it('should project .form-section-footer content only when focused and then change edit state', () => {
        expect(comp.getFormState()).toBe('normal');
        const footer: NodeListOf<Element> = el.querySelectorAll('vdk-form-section span.form-section-footer');
        expect(footer.length).toBe(0);
        fixture.componentInstance.focused = true;
        fixture.detectChanges();
        expect(comp.getFormState()).toBe('edit');
        const footers: NodeListOf<Element> = el.querySelectorAll('vdk-form-section span.form-section-footer');
        expect(footers.length).toBe(1);
    });
});
