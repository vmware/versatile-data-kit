/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApolloError } from '@apollo/client/core';

import { CollectionsUtil } from '@vdk/shared';

/**
 * ** Error Utils class.
 *
 * @author gorankokin
 */
export class ErrorUtil {
    /**
     * ** Extract root Error depending of the format.
     */
    static extractError(error: Error): Error {
        if (
            error instanceof ApolloError &&
            CollectionsUtil.isDefined(error.networkError)
        ) {
            return error.networkError;
        }

        return error;
    }
}
