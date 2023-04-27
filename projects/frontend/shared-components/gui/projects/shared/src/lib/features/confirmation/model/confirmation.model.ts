/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Type } from '@angular/core';

import { CollectionsUtil, Mutable } from '../../../utils';

export const ERROR_CODE_CONFIRMATION_FORCEFULLY_DESTROYED_COMPONENT = 'EC_CONFIRMATION_1000';

/**
 * ** Confirmation Input Model.
 *
 *      - Model instance provided as input instructions for Confirmation Service, or to more specific to method {@link ConfirmationService.confirm}
 *      - Most of the fields are optional and Model Impl provides its own defaults.
 */
export interface ConfirmationInputModel extends SupportedButtonsModel, SupportedMessageModel {
    /**
     * ** Confirmation title.
     *
     *      - Service render provided content as innerHTML.
     *      - HTML tags could be provided in string template.
     */
    title?: string;
    /**
     * ** Whether confirmation view to render close X button in top right corner.
     */
    closable?: boolean;
    /**
     * ** Whether confirmation view to render option for User to opt-out of showing confirmations with same context in the future.
     */
    optionDoNotShowFutureConfirmation?: boolean;
}

/**
 * ** Confirmation Input Model extension for the needs of {@link ConfirmationService}.
 *
 *      - private model used only in the service.
 */
export interface ConfirmationModelExtension {
    /**
     * ** Model UUID.
     */
    uuid: string;
    /**
     * ** Confirmation Handler.
     */
    handler: ConfirmationHandler;
}

/**
 * ** Supported Confirmation view Messages, providing one of the bellow options.
 *
 *      - it could be text provided with html tags inside
 *      - it could be Component class ref with optional messageCode
 */
export interface SupportedMessageModel {
    /**
     * ** Confirmation message.
     *
     *      - Service render provided content as innerHTML.
     *      - HTML tags could be provided in string template.
     */
    message?: string;
    /**
     * ** Confirmation message component.
     *
     *      - Service render provided component in the same place where message text is rendered.
     *      - Message Component takes precedence before message text. e.g. if both fields are provided, Service will render the Component.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    messageComponent?: Type<any>;
    /**
     * ** Confirmation message code, that would be injected to Message component in initialization time
     *      before first changeDetection in order to re-use same component for different messages.
     */
    messageCode?: string;
}

/**
 * ** Supported Confirmation View Buttons.
 */
export interface SupportedButtonsModel {
    /**
     * ** Model for Confirmation Cancel Button.
     *
     *      - Providing Cancel button model, means this button should be rendered.
     */
    cancelBtnModel?: Partial<ButtonModel>;
    /**
     * ** Model for Confirmation Confirm Button.
     */
    confirmBtnModel?: ButtonModel;
}

/**
 * ** Generic Button Model in Confirmation view.
 */
export interface ButtonModel {
    /**
     * ** Button text.
     */
    text: string;
    /**
     * ** Button icon shape.
     */
    iconShape?: string;
    /**
     * ** Button icon position.
     */
    iconPosition?: 'left' | 'right';
    /**
     * ** Button icon direction.
     */
    iconDirection?: 'up' | 'down' | 'left' | 'right';
    /**
     * ** Button icon size.
     */
    iconSize?: string | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
    /**
     * ** Button icon solid.
     */
    iconSolid?: boolean;
    /**
     * ** Button icon inverse.
     */
    iconInverse?: boolean;
    /**
     * ** Button icon status.
     */
    iconStatus?: 'info' | 'success' | 'warning' | 'danger';
    /**
     * ** Button icon badge.
     */
    iconBadge?: 'info' | 'success' | 'warning' | 'danger';
}

/**
 * ** Confirmation Model implementation that leverage input model and model extension.
 */
export class ConfirmationModelImpl implements ConfirmationInputModel, ConfirmationModelExtension {
    /**
     * @inheritDoc
     */
    readonly uuid: string;
    /**
     * @inheritDoc
     *
     *      - By default it's empty.
     */
    readonly title?: string;
    /**
     * @inheritDoc
     *
     *      - By default it's empty.
     */
    readonly message?: string;
    /**
     * @inheritDoc
     *
     *      - By default is undefined.
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    readonly messageComponent?: Type<any>;
    /**
     * @inheritDoc
     *
     *      - By default it's empty.
     */
    messageCode?: string;
    /**
     * @inheritDoc
     *
     *      - By default its FALSE.
     */
    readonly closable?: boolean;
    /**
     * @inheritDoc
     *
     *      - By default its FALSE.
     */
    readonly optionDoNotShowFutureConfirmation?: boolean;
    /**
     * @inheritDoc
     *
     *      - By default its text is Cancel.
     */
    readonly cancelBtnModel?: Readonly<ButtonModel>;
    /**
     * @inheritDoc
     *
     *      - By default its text is Confirm.
     */
    readonly confirmBtnModel?: Readonly<ButtonModel>;
    /**
     * @inheritDoc
     */
    readonly handler: ConfirmationHandler;

    /**
     * ** Constructor.
     */
    constructor(model: ConfirmationInputModel) {
        // assign provided model to model class fields
        Object.assign(this, model ?? {});

        // assign UUID
        this.uuid = CollectionsUtil.generateUUID();

        // initialize handler ref
        if (CollectionsUtil.isNil(this.handler)) {
            this.handler = {
                confirm: null,
                dismiss: null
            };
        }

        // check if value exist, otherwise set to default FALSE
        if (CollectionsUtil.isNil(this.closable)) {
            this.closable = false;
        }

        // check if value exist, otherwise set to default FALSE
        if (CollectionsUtil.isNil(this.optionDoNotShowFutureConfirmation)) {
            this.optionDoNotShowFutureConfirmation = false;
        }

        // confirm button model
        this._assignButtonModelDefaults('confirmBtnModel', 'Confirm');

        // cancel button model
        if (CollectionsUtil.isObjectNotNull(this.cancelBtnModel)) {
            this._assignButtonModelDefaults('cancelBtnModel', 'Cancel');
        } else {
            this.cancelBtnModel = null;
        }
    }

    private _assignButtonModelDefaults(modelKey: keyof SupportedButtonsModel, defaultText: string): void {
        // when there is no model set default text only, and return flow to invoker
        if (CollectionsUtil.isNil(this[modelKey])) {
            (this[modelKey] as Mutable<ButtonModel>) = {
                text: defaultText
            };

            return;
        }

        // if model exist but there is no text, set default one, and continue further
        if (!CollectionsUtil.isStringWithContent(this[modelKey].text)) {
            (this[modelKey] as Mutable<ButtonModel>).text = defaultText;
        }

        // if model exist check if there is no icon shape, and return flow to invoker
        if (!this[modelKey].iconShape) {
            (this[modelKey] as Mutable<ButtonModel>).iconShape = null;
            (this[modelKey] as Mutable<ButtonModel>).iconPosition = null;

            return;
        }

        // if model exist check if there is no position set or position is something unsupported and set default one to 'left'
        if (!this[modelKey].iconPosition || (this[modelKey].iconPosition !== 'left' && this[modelKey].iconPosition !== 'right')) {
            (this[modelKey] as Mutable<ButtonModel>).iconPosition = 'left';
        }
    }
}

/**
 * ** Confirmation Output Model.
 *
 *      - Returned to invoker after User confirmation.
 */
export interface ConfirmationOutputModel {
    /**
     * ** Field value of true, means User opt-out of showing confirmations with same context in the future.
     */
    doNotShowFutureConfirmation: boolean;
}

/**
 * ** Confirmation handler.
 */
export interface ConfirmationHandler {
    /**
     * ** Confirm method, which means User give confirmation.
     */
    confirm: (value: ConfirmationOutputModel) => void;
    /**
     * ** Dismiss (reject) method, which means User don't give confirmation.
     */
    dismiss: (reason?: string | Error) => void;
}
