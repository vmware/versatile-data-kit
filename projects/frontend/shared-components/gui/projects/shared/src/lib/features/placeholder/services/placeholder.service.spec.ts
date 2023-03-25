/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @angular-eslint/component-selector,
                  @angular-eslint/component-class-suffix,
                  @typescript-eslint/restrict-template-expressions,
                  @typescript-eslint/no-unsafe-member-access */

import { Component, CUSTOM_ELEMENTS_SCHEMA, DebugElement, ElementRef, HostListener, OnInit, Renderer2 } from '@angular/core';
import { HttpErrorResponse, HttpStatusCode } from '@angular/common/http';
import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

import { CollectionsUtil } from '../../../utils';

import { ApiErrorMessage, ErrorRecord, generateErrorCode } from '../../../common';

import { PlaceholderService } from './placeholder.service';

@Component({
    selector: 'shared-placeholder',
    template: `
        <div>
            <p>Some placeholder</p>
        </div>
    `,
    providers: [PlaceholderService]
})
class PlaceholderComponentStub implements OnInit {
    @HostListener('changeHideDefaultStateImageInGrid', ['$event']) changeHideImageInGrid($event: { value: boolean }) {
        this._hideDefaultEmptyStateImageInGrid = $event.value;

        this._executeRefineCycle();
    }

    private _hideDefaultEmptyStateImageInGrid = false;

    constructor(
        public readonly elementRef: ElementRef<HTMLElement>,
        public readonly renderer2: Renderer2,
        private readonly placeholderService: PlaceholderService
    ) {}

    ngOnInit(): void {
        this._executeRefineCycle();
    }

    private _executeRefineCycle(): void {
        this.placeholderService.refineElementsState(this.elementRef, this._hideDefaultEmptyStateImageInGrid);
    }
}

@Component({
    selector: 'clr-datagrid',
    template: `
        <div>
            <div>
                <div class="placeholder-container">
                    <shared-placeholder></shared-placeholder>
                </div>
            </div>
        </div>
    `
})
class ClarityDataGridComponentStub {
    constructor(public readonly elementRef: ElementRef<HTMLElement>) {}
}

@Component({
    selector: 'shared-container',
    template: `
        <div class="placeholder-container">
            <shared-placeholder></shared-placeholder>
        </div>
    `
})
class StandaloneComponentStub {
    constructor(public readonly elementRef: ElementRef<HTMLElement>) {}
}

@Component({
    selector: 'test-component',
    template: `
        <div>
            <clr-datagrid></clr-datagrid>
        </div>
    `
})
class TestComponentStub {}

describe('PlaceholderService', () => {
    let randomStringGrid: string;
    let randomStringStandalone: string;

    let fixture: ComponentFixture<TestComponentStub>;

    let gridDebugElement: DebugElement;
    let gridComponent: ClarityDataGridComponentStub;

    let placeholderDebugElement: DebugElement;
    let placeholderComponent: PlaceholderComponentStub;

    let renderer2: Renderer2;

    let service: PlaceholderService;

    beforeEach(() => {
        randomStringGrid = 'fsklmxksfdksaj';
        randomStringStandalone = 'dsaasdfsdffff';
        spyOn(CollectionsUtil, 'generateRandomString').and.returnValues(
            randomStringGrid,
            randomStringStandalone,
            randomStringGrid,
            randomStringStandalone
        );

        TestBed.configureTestingModule({
            declarations: [PlaceholderComponentStub, ClarityDataGridComponentStub, TestComponentStub],
            providers: [Renderer2],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        });

        fixture = TestBed.createComponent(TestComponentStub);

        gridDebugElement = fixture.debugElement.query(By.directive(ClarityDataGridComponentStub));
        gridComponent = gridDebugElement.componentInstance;

        placeholderDebugElement = fixture.debugElement.query(By.directive(PlaceholderComponentStub));
        placeholderComponent = placeholderDebugElement.componentInstance;

        renderer2 = placeholderComponent.renderer2;

        service = placeholderDebugElement.injector.get(PlaceholderService);
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            let errorCodes: string[];
            let errorRecords: ErrorRecord[];

            beforeEach(() => {
                errorCodes = [
                    generateErrorCode(PlaceholderService.CLASS_NAME, PlaceholderService.PUBLIC_NAME, 'refineElementsState', '500'),
                    generateErrorCode(PlaceholderService.CLASS_NAME, PlaceholderService.PUBLIC_NAME, 'refineElementsState', '503'),
                    generateErrorCode('DataLoadApiService', 'Data-Load-Api-Service', 'loadData', '422')
                ];
                errorRecords = [
                    {
                        code: errorCodes[0],
                        error: new HttpErrorResponse({
                            error: new Error('Some Error 1'),
                            status: 500
                        }),
                        httpStatusCode: 500,
                        objectUUID: 'SomeObjectUUID_1'
                    },
                    {
                        code: errorCodes[1],
                        error: new HttpErrorResponse({
                            error: new Error('Some Error 2'),
                            status: 503
                        }),
                        httpStatusCode: 503,
                        objectUUID: 'SomeObjectUUID_1'
                    },
                    {
                        code: errorCodes[2],
                        error: new HttpErrorResponse({
                            error: new Error('Some Error 3'),
                            status: 422
                        }),
                        httpStatusCode: 422,
                        objectUUID: 'SomeObjectUUID_2'
                    }
                ];
            });

            describe('|extractClassPublicName|', () => {
                it('should verify will extract Class Public Name', () => {
                    // When
                    const publicName1 = PlaceholderService.extractClassPublicName(errorRecords[0]);
                    const publicName2 = PlaceholderService.extractClassPublicName(errorRecords[1]);
                    const publicName3 = PlaceholderService.extractClassPublicName(errorRecords[2]);
                    const publicName4 = PlaceholderService.extractClassPublicName(null);

                    // Then
                    expect(publicName1).toEqual('Placeholder service');
                    expect(publicName2).toEqual('Placeholder service');
                    expect(publicName3).toEqual('Data load api service');
                    expect(publicName4).toEqual('');
                });
            });

            describe('|extractClassesPublicNames|', () => {
                it('should verify will extract Class Public Names of multiple ErrorRecord', () => {
                    // When
                    const publicNames = PlaceholderService.extractClassesPublicNames(errorRecords);

                    // Then
                    expect(publicNames).toEqual('Placeholder service, Data load api service');
                });
            });
        });
    });

    describe('Methods::', () => {
        describe('|refineElementsState|', () => {
            it('should verify method would be invoked from stub Component upon change detection', () => {
                // Given
                const spyMethod = spyOn(service, 'refineElementsState').and.callThrough();

                // When
                fixture.detectChanges();

                // Then
                expect(spyMethod).toHaveBeenCalledWith(placeholderComponent.elementRef, false);
            });

            it('should verify will append styling in head', fakeAsync(() => {
                // When
                fixture.detectChanges();

                tick(2000);

                // Then
                const styleElementGrid = document.querySelector(`head style[data-shared-grid-style="${randomStringGrid}"]`);
                const styleElementStandalone = document.querySelector(
                    `head style[data-shared-placeholder-style="${randomStringStandalone}"]`
                );

                expect(styleElementGrid).toBeDefined();
                expect(styleElementGrid.innerHTML.trim().replace(/\s/g, '')).toEqual(
                    `
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder.datagrid-empty {
                            justify-content: center;
                        }
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder-image {
                            display: block;
                        }
                    `
                        .trim()
                        .replace(/\s/g, '')
                );

                expect(styleElementStandalone).toBeNull();
            }));

            it('should verify wont append styling in head if grid is not found', fakeAsync(() => {
                // Given
                const spyRenderer2ParentNode = spyOn(renderer2, 'parentNode').and.returnValue(null);

                // When
                fixture.detectChanges();

                tick(8000);

                // Then
                const styleElementGrid = document.querySelector(`head style[data-shared-grid-style="${randomStringGrid}"]`);
                expect(styleElementGrid).toEqual(null);
                expect(spyRenderer2ParentNode).toHaveBeenCalledTimes(200);
            }), 10000);

            it('should verify will append styling in head if element is standalone', fakeAsync(() => {
                // Given
                spyOn(renderer2, 'parentNode').and.returnValue(null);

                // When
                fixture.detectChanges();

                tick(8000);

                // Then
                const styleElementStandalone = document.querySelector(
                    `head style[data-shared-placeholder-style="${randomStringStandalone}"]`
                );

                expect(styleElementStandalone).toBeDefined();
                expect(styleElementStandalone.innerHTML.trim().replace(/\s/g, '')).toEqual(
                    `
                        shared-placeholder[data-shared-placeholder="${randomStringStandalone}"] {
                            margin-top: 5rem;
                        }
                    `
                        .trim()
                        .replace(/\s/g, '')
                );
            }), 10000);

            it('should verify will toggle appended styling in head depending of provided flag to method', fakeAsync(() => {
                // When 1
                fixture.detectChanges();

                tick(2000);

                // Then 1
                const styleElement = document.querySelector(`head style[data-shared-grid-style="${randomStringGrid}"]`);

                expect(styleElement).toBeDefined();
                expect(styleElement.innerHTML.trim().replace(/\s/g, '')).toEqual(
                    `
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder.datagrid-empty {
                            justify-content: center;
                        }
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder-image {
                            display: block;
                        }
                    `
                        .trim()
                        .replace(/\s/g, '')
                );

                // When 2
                placeholderDebugElement.triggerEventHandler('changeHideDefaultStateImageInGrid', { value: true });

                tick(2000);

                // Then 2
                expect(styleElement.innerHTML.trim().replace(/\s/g, '')).toEqual(
                    `
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder.datagrid-empty {
                            justify-content: center;
                        }
                        clr-datagrid[data-shared-grid="${randomStringGrid}"] clr-dg-placeholder .datagrid-placeholder-image {
                            display: none;
                        }
                    `
                        .trim()
                        .replace(/\s/g, '')
                );
            }));

            it('should verify will append data attribute to grid component when found', fakeAsync(() => {
                // When
                fixture.detectChanges();

                tick(2000);

                // Then
                expect(gridComponent.elementRef.nativeElement.hasAttribute('data-shared-grid')).toBeTrue();
                expect(gridComponent.elementRef.nativeElement.getAttribute('data-shared-grid')).toEqual(randomStringGrid);
            }));

            it('should verify wont append data attribute to grid component if it cannot find', fakeAsync(() => {
                // Given
                const spyRenderer2ParentNode = spyOn(renderer2, 'parentNode').and.returnValue(null);

                // When
                fixture.detectChanges();

                tick(8000);

                // Then
                expect(gridComponent.elementRef.nativeElement.hasAttribute('data-shared-grid')).toBeFalse();
                expect(spyRenderer2ParentNode).toHaveBeenCalledTimes(200);
            }), 10000);

            it('should verify wont append data attribute to grid component if it cannot find due to greater placeholder depth of 15', fakeAsync(() => {
                // Given
                TestBed.resetTestingModule()
                    .configureTestingModule({
                        declarations: [TestComponentStub, PlaceholderComponentStub, ClarityDataGridComponentStub],
                        providers: [Renderer2]
                    })
                    .overrideComponent(ClarityDataGridComponentStub, {
                        set: {
                            template: `
                            <div>
                                <div>
                                    <div>
                                        <div>
                                            <div>
                                                <div>
                                                    <div>
                                                        <div>
                                                            <div>
                                                                <div>
                                                                    <div>
                                                                        <div>
                                                                            <div>
                                                                                <div>
                                                                                    <div class="placeholder-container">
                                                                                        <shared-placeholder></shared-placeholder>
                                                                                    </div>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `
                        }
                    });

                // When
                fixture = TestBed.createComponent(TestComponentStub);

                gridDebugElement = fixture.debugElement.query(By.directive(ClarityDataGridComponentStub));
                gridComponent = gridDebugElement.componentInstance;

                fixture.detectChanges();

                tick(2000);

                // Then
                expect(gridComponent.elementRef.nativeElement.hasAttribute('data-shared-grid')).toBeFalse();
            }));

            it('should verify will append data attribute to placeholder when is standalone', fakeAsync(() => {
                // Given
                TestBed.resetTestingModule()
                    .configureTestingModule({
                        declarations: [PlaceholderComponentStub, StandaloneComponentStub, TestComponentStub],
                        providers: [Renderer2]
                    })
                    .overrideComponent(TestComponentStub, {
                        set: {
                            template: `
                            <div>
                                <shared-container></shared-container>
                            </div>
                        `
                        }
                    });

                // When
                fixture = TestBed.createComponent(TestComponentStub);

                placeholderDebugElement = fixture.debugElement.query(By.directive(PlaceholderComponentStub));
                placeholderComponent = placeholderDebugElement.componentInstance;

                fixture.detectChanges();

                tick(4000);

                // Then
                expect(placeholderComponent.elementRef.nativeElement.hasAttribute('data-shared-placeholder')).toBeTrue();
                expect(placeholderComponent.elementRef.nativeElement.getAttribute('data-shared-placeholder')).toEqual(
                    randomStringStandalone
                );
            }));
        });

        describe('|extractErrorInformation|', () => {
            describe('parameterized_test', () => {
                const errors: HttpErrorResponse[] = [
                    new HttpErrorResponse({
                        status: HttpStatusCode.InternalServerError,
                        error: `Something bad happened and it's string`
                    }),
                    new HttpErrorResponse({
                        status: HttpStatusCode.InternalServerError,
                        error: {
                            what: `text what`,
                            why: `text why`,
                            consequences: `text consequences`,
                            countermeasures: `text countermeasures`
                        }
                    }),
                    new HttpErrorResponse({
                        status: HttpStatusCode.InternalServerError,
                        error: null
                    }),
                    new HttpErrorResponse({
                        status: HttpStatusCode.BadGateway,
                        error: undefined
                    }),
                    new SyntaxError('Unsupported Action') as HttpErrorResponse
                ];
                const params: Array<[string, Error, ApiErrorMessage]> = [
                    [
                        'error is HttpErrorResponse and nested error is string',
                        errors[0],
                        { what: `${errors[0].error}`, why: `${errors[0].message}` }
                    ],
                    [
                        'error is HttpErrorResponse and nested error is formatted ApiErrorMessage',
                        errors[1],
                        {
                            what: `${errors[1].error.what}`,
                            why: `${errors[1].error.why}`,
                            consequences: `${errors[1].error.consequences}`,
                            countermeasures: `${errors[1].error.countermeasures}`
                        }
                    ],
                    [
                        'error is HttpErrorResponse and nested error is null',
                        errors[2],
                        {
                            what: 'Please contact Superollider and report the issue',
                            why: 'Internal Server Error'
                        }
                    ],
                    [
                        'error is HttpErrorResponse and nested error is undefined',
                        errors[3],
                        {
                            what: 'Please contact Superollider and report the issue',
                            why: 'Unknown Error'
                        }
                    ],
                    [
                        'error is not HttpErrorResponse',
                        errors[4],
                        {
                            what: 'Please contact Superollider and report the issue',
                            why: 'Unknown Error'
                        }
                    ]
                ];

                for (const [description, error, assertion] of params) {
                    it(`should verify will return ApiErrorMessage when ${description}`, () => {
                        // When
                        const apiMessage = service.extractErrorInformation(error);

                        // Then
                        expect(apiMessage).toEqual(assertion);
                    });
                }
            });
        });
    });
});
