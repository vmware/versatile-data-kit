/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ElementRef, Renderer2 } from '@angular/core';

import { AttributesDirective } from './attribute.directive';

describe('AttributesDirective', () => {
    let nativeElementStub: any;
    let elementRefStub: ElementRef;
    let rendererStub: jasmine.SpyObj<Renderer2>;

    let directive: AttributesDirective;

    beforeEach(() => {
        nativeElementStub = {};
        elementRefStub = {
            nativeElement: nativeElementStub
        };
        rendererStub = jasmine.createSpyObj<Renderer2>('renderer2', ['setAttribute', 'removeAttribute']);

        directive = new AttributesDirective(elementRefStub, rendererStub);
    });

    it('should verify directive instance is created', () => {
        // Then
        expect(directive).toBeDefined();
    });

    it('should verify on no attributes wont execute renderer', () => {
        // When
        directive.ngOnChanges({});
        directive.ngOnInit();

        // Then
        expect(rendererStub.setAttribute).not.toHaveBeenCalled();
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();
    });

    it('should verify when attributes are null wont execute renderer', () => {
        // When
        directive.attributes = null;
        directive.ngOnChanges({});
        directive.ngOnInit();

        // Then
        expect(rendererStub.setAttribute).not.toHaveBeenCalled();
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();
    });

    it('should verify when attributes are not Literal Object wont execute renderer', () => {
        // When
        directive.attributes = new Map() as any;
        directive.ngOnChanges({});
        directive.ngOnInit();

        // Then
        expect(rendererStub.setAttribute).not.toHaveBeenCalled();
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();
    });

    it('should verify when providing two times same attributes by value but different reference would execute only once', () => {
        // When 1
        directive.attributes = {
            title: 'some-title',
            size: 10,
            shape: 'square',
            class: 'css-class-1, css-class-2, css-class-3',
            tabIndex: 0,
            'data-cy': 'cypress-selector'
        };
        directive.ngOnInit();

        // Then 1
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(6);
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();

        // When 2
        directive.attributes = {
            title: 'some-title',
            size: 10,
            shape: 'square',
            class: 'css-class-1, css-class-2, css-class-3',
            tabIndex: 0,
            'data-cy': 'cypress-selector'
        };
        directive.ngOnChanges({});

        // Then
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(6);
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();
    });

    it('should verify will set expected attributes from provided Literal Object', () => {
        // When
        directive.attributes = {
            title: 'element-title',
            size: 10,
            shape: 'square',
            class: 'css-class-1, css-class-2, css-class-3',
            'aria-label': 'aria-element-title',
            tabIndex: 0,
            'data-cy': 'cypress-selector'
        };
        directive.ngOnInit();

        // Then
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(7);
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();
    });

    it('should verify will remove expected attributes from provided Literal Object', () => {
        // When
        directive.attributes = {
            title: undefined,
            size: 10,
            shape: 'square',
            class: 'css-class-1, css-class-2, css-class-3',
            'aria-label': null,
            tabIndex: 0,
            'data-cy': 'cypress-selector',
            'data-index': false,
            'data-attribute': 'delete',
            'data-btn': 'false',
            'data-attr': ''
        };
        directive.ngOnInit();

        // Then
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(5);
        expect(rendererStub.removeAttribute).toHaveBeenCalledTimes(6);
    });

    it('should verify will set and then remove provided attributes', () => {
        // When 1
        directive.attributes = {
            title: 'some-title',
            size: 10,
            shape: 'square',
            class: 'css-class-1, css-class-2, css-class-3',
            tabIndex: 0,
            'data-cy': 'cypress-selector'
        };
        directive.ngOnInit();

        // Then 1
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(6);
        expect(rendererStub.removeAttribute).not.toHaveBeenCalled();

        // When 2
        directive.attributes = null;
        directive.ngOnChanges({});

        // Then 2
        expect(rendererStub.setAttribute).toHaveBeenCalledTimes(6);
        expect(rendererStub.removeAttribute).toHaveBeenCalledTimes(6);
    });
});
