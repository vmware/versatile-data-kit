
/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ViewChild, Component } from '@angular/core';
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';

import { ClarityModule } from "@clr/angular";

import { VdkCopyToClipboardButtonComponent } from './copy-to-clipboard-button.component';

describe('CopyToClipboardButtonComponent', () => {
    let component: VdkCopyToClipboardButtonComponent;
    let hostComponent: TestHostComponent;
    let fixture: ComponentFixture<TestHostComponent>;
    let element: any;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                ClarityModule,
            ],
            declarations: [
                TestHostComponent,
                VdkCopyToClipboardButtonComponent
            ]
        });
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(TestHostComponent);
        element = fixture.debugElement.nativeElement;
        hostComponent = fixture.componentInstance;
        component = hostComponent.component;
    });

    describe('when no btnLabel specified', () => {
        beforeEach(() => {
            fixture.detectChanges();
        });

        it('should initialize size properly', () => {
            component.ngOnInit();
            expect(component.bounds).toBe('22px');
            component.size = 24;
            component.ngOnInit();
            expect(component.bounds).toBe('30px');
        });

        it('should copy the value to the clipboard', () => {
            spyOn(component, 'copyToClipboard');
            component.doCopy();
            expect(component.copyToClipboard).toHaveBeenCalledWith('Test string');
        });

        it('should set the proper "copied" status', fakeAsync(() => {
            component.doCopy();
            expect(component.copied).toBeTruthy();
            tick(1500);
            expect(component.copied).toBeFalsy();
        }));

        // it('should show the copy icon', () => {
        //     expect(element).toHaveRendered('.copy-button');
        // });

        // it('should not show the copy button with text', () => {
        //     expect(element).not.toHaveRendered('button.btn.btn-outline');
        // });
    });

    // describe('when btnLabel specified', () => {
    //     beforeEach(() => {
    //         component.btnLabel = 'COPY TO CLIPBOARD';
    //         fixture.detectChanges();
    //     });
    //
    //     it('should show the copy button with text', () => {
    //         expect(element).toHaveRendered('button.btn.btn-outline');
    //
    //         let label = element.querySelector('button .face-label span');
    //         expect(label.innerText.trim()).toEqual('COPY TO CLIPBOARD');
    //     });
    // });
});

@Component({
    template: `
        <vdk-copy-to-clipboard-button
            [value]="value">
        </vdk-copy-to-clipboard-button>
    `
})
class TestHostComponent {
    @ViewChild(VdkCopyToClipboardButtonComponent, { static: true }) component: VdkCopyToClipboardButtonComponent;

    public value = 'Test string';
}
