

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    COMPONENT_CLEAR_DATA,
    COMPONENT_FAILED,
    COMPONENT_IDLE,
    COMPONENT_INIT,
    COMPONENT_LOADED,
    COMPONENT_LOADING,
    COMPONENT_UPDATE,
    ComponentClearData,
    ComponentFailed,
    ComponentIdle,
    ComponentInit,
    ComponentLoaded,
    ComponentLoading,
    ComponentUpdate
} from './component.actions';
import { ComponentStateImpl } from '../../model';
import { BaseAction, BaseActionWithPayload } from '../../../ngrx';

describe('ComponentActions', () => {
    describe('ComponentInit', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentInit(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentInit(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_INIT);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentInit(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentInit.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentInit);
                    });
                });
            });
        });
    });

    describe('ComponentIdle', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentIdle(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentIdle(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_IDLE);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentIdle(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentIdle.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentIdle);
                    });
                });
            });
        });
    });

    describe('ComponentLoading', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentLoading(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentLoading(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_LOADING);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentLoading(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentLoading.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentLoading);
                    });
                });
            });
        });
    });

    describe('ComponentLoaded', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentLoaded(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentLoaded(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_LOADED);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentLoaded(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentLoaded.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentLoaded);
                    });
                });
            });
        });
    });

    describe('ComponentFailed', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentFailed(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentFailed(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_FAILED);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentFailed(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentFailed.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentFailed);
                    });
                });
            });
        });
    });

    describe('ComponentUpdate', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentUpdate(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentUpdate(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_UPDATE);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentUpdate(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentUpdate.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentUpdate);
                    });
                });
            });
        });
    });

    describe('ComponentClearData', () => {
        it('should verify instance is created', () => {
            // Then
            expect(() => new ComponentClearData(ComponentStateImpl.of({}))).toBeDefined();
        });

        it('should verify correct type is assigned', () => {
            // When
            const instance = new ComponentClearData(ComponentStateImpl.of({}));

            // Then
            expect(instance.type).toEqual(COMPONENT_CLEAR_DATA);
        });

        it('should verify prototype chaining', () => {
            // When
            const instance = new ComponentClearData(ComponentStateImpl.of({}));

            // Then
            expect(instance).toBeInstanceOf(BaseActionWithPayload);
            expect(instance).toBeInstanceOf(BaseAction);
        });

        describe('Statics::', () => {
            describe('Methods::', () => {
                describe('|of|', () => {
                    it('should verify factory method will create instance', () => {
                        // When
                        const instance = ComponentClearData.of(ComponentStateImpl.of({}));

                        // Then
                        expect(instance).toBeInstanceOf(ComponentClearData);
                    });
                });
            });
        });
    });
});
