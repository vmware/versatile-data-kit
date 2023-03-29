/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA, ElementRef, Renderer2 } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SHARED_FEATURES_CONFIG_TOKEN } from '../../_token';

import { PlaceholderConfig } from '../model';

import { PlaceholderComponent } from './placeholder.component';

describe('PlaceholderComponent', () => {
    let serviceRequestUrl: string;
    let elementRefFake: ElementRef;
    let renderer2Stub: jasmine.SpyObj<Renderer2>;

    let component: PlaceholderComponent;
    let fixture: ComponentFixture<PlaceholderComponent>;

    beforeEach(async () => {
        elementRefFake = {
            nativeElement: null
        };
        renderer2Stub = jasmine.createSpyObj<Renderer2>('renderer2Stub', [
            'removeChild',
            'parentNode',
            'createElement',
            'setAttribute',
            'appendChild'
        ]);

        await TestBed.configureTestingModule({
            declarations: [PlaceholderComponent],
            providers: [
                { provide: ElementRef, useValue: elementRefFake },
                { provide: Renderer2, useValue: renderer2Stub },
                { provide: SHARED_FEATURES_CONFIG_TOKEN, useValue: { placeholder: { serviceRequestUrl } } as PlaceholderConfig }
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        }).compileComponents();
    });

    beforeEach(() => {
        serviceRequestUrl = 'https://service-url';

        fixture = TestBed.createComponent(PlaceholderComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
