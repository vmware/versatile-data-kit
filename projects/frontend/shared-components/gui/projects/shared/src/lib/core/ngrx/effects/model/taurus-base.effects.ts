/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive } from '@angular/core';

import { Actions } from '@ngrx/effects';

import { TaurusObject } from '../../../../common';

import { ComponentService } from '../../../component';

/**
 * ** Base class for all NgRx Effects.
 */
@Directive()
export abstract class TaurusBaseEffects extends TaurusObject {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'TaurusBaseEffects';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'Taurus-Base-Effects';

    /**
     * ** Constructor.
     *
     * @protected
     */
    protected constructor(
        protected readonly actions$: Actions,
        protected readonly componentService: ComponentService,
        className?: string
    ) {
        super(className ?? TaurusBaseEffects.CLASS_NAME);
    }

    /**
     * ** Implement this method and register all error codes that could be recorded from Class effects.
     *
     *      - Bound error codes to error-codes repository when keys are tasks name and value is all available error codes for that particular task.
     *      - Implement in subclasses and invoke in Constructor to register Effects Error Codes.
     *
     * @protected
     */
    protected abstract registerEffectsErrorCodes(): void;
}
