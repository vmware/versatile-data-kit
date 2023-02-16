

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Literal } from '../../interfaces';
import { CollectionsUtil } from '../../../utils';

// Page DTO

export type LiteralRequestPage = { pageNumber: number; pageSize: number };

export interface RequestPage extends Literal<LiteralRequestPage> {
    readonly page: number;
    readonly size: number;
}

/**
 * ** Request Page DTO.
 *
 *
 */
export class RequestPageImpl implements RequestPage {
    public readonly page: number;
    public readonly size: number;

    constructor(page: number, size: number) {
        this.page = page ?? 1;
        this.size = size ?? 25;
    }

    /**
     * ** Factory method.
     */
    static of(page: number, size: number): RequestPageImpl {
        return new RequestPageImpl(page, size);
    }

    /**
     * ** Factory method for empty RequestPageDTO.
     */
    static empty(): RequestPageImpl {
        return new RequestPageImpl(null, null);
    }

    /**
     * ** Creates DTO from literal.
     */
    static fromLiteral(literalDTO: { pageNumber: number; pageSize: number }): RequestPageImpl {
        return RequestPageImpl.of(literalDTO.pageNumber, literalDTO.pageSize);
    }

    /**
     * @inheritDoc
     */
    toLiteral(): LiteralRequestPage {
        return {
            pageNumber: this.page ?? 1,
            pageSize: this.size ?? 25
        };
    }

    /**
     * @inheritDoc
     */
    toLiteralDeepClone(): LiteralRequestPage {
        return this.toLiteral();
    }
}

// Order DTO

export interface RequestOrder extends Literal<LiteralApiPredicates> {
    readonly criteria: ApiPredicate[];
}

/**
 * ** Request Order DTO.
 *
 *
 */
export class RequestOrderImpl implements RequestOrder {
    public readonly criteria: ApiPredicate[];

    constructor(...criteria: ApiPredicate[]) {
        // eslint-disable-next-line @typescript-eslint/unbound-method
        this.criteria = [...criteria.filter(CollectionsUtil.isDefined)];
    }

    /**
     * ** Factory method.
     */
    static of(...criteria: ApiPredicate[]): RequestOrderImpl {
        return new RequestOrderImpl(...criteria);
    }

    /**
     * ** Factory method for empty RequestOrderDTO.
     */
    static empty(): RequestOrderImpl {
        return new RequestOrderImpl();
    }

    /**
     * ** Creates DTO from literal.
     */
    static fromLiteral(literalCriteria: Array<ApiPredicate>): RequestOrderImpl {
        return RequestOrderImpl.of(...literalCriteria);
    }

    /**
     * @inheritDoc
     */
    toLiteral(): LiteralApiPredicates {
        return [...this.criteria];
    }

    /**
     * @inheritDoc
     */
    toLiteralDeepClone(): LiteralApiPredicates {
        return this.criteria
                   .map((c) => ({ ...c }));
    }
}

// Filter DTO

export interface RequestFilter extends Literal<LiteralApiPredicates> {
    readonly criteria: ApiPredicate[];
}

/**
 * ** Request Filter DTO.
 *
 *
 */
export class RequestFilterImpl implements RequestFilter {
    public readonly criteria: ApiPredicate[];

    constructor(...criteria: ApiPredicate[]) {
        // eslint-disable-next-line @typescript-eslint/unbound-method
        this.criteria = [...criteria.filter(CollectionsUtil.isDefined)];
    }

    /**
     * ** Factory method.
     */
    static of(...criteria: ApiPredicate[]): RequestFilterImpl {
        return new RequestFilterImpl(...criteria);
    }

    /**
     * ** Factory method for empty RequestFilterDTO.
     */
    static empty(): RequestFilterImpl {
        return new RequestFilterImpl();
    }

    /**
     * ** Creates DTO from literal.
     */
    static fromLiteral(literalCriteria: Array<ApiPredicate>): RequestFilterImpl {
        return RequestFilterImpl.of(...literalCriteria);
    }

    /**
     * @inheritDoc
     */
    toLiteral(): LiteralApiPredicates {
        return [...this.criteria];
    }

    /**
     * @inheritDoc
     */
    toLiteralDeepClone(): LiteralApiPredicates {
        return this.criteria
                   .map((c) => ({ ...c }));
    }
}

// Generic Predicate for API

export type LiteralApiPredicates = Array<ApiPredicate>;

export const ASC = 'ASC';
export const DESC = 'DESC';
export type DirectionType = typeof ASC | typeof DESC;

export interface ApiPredicate {
    readonly property: string;
    readonly pattern: string;
    readonly sort: DirectionType;
}
