import { HttpErrorResponse } from '@angular/common/http';

import { VmwToastType } from '../../../commons';

export interface Toast {
    title: string;
    description: string;
    type: VmwToastType;
    error?: Error | FormattedError | HttpErrorResponse;
    expanded?: boolean;
    responseStatus?: number;
    extendedData?: {
        title: string;
        description: string;
    };
}

export interface FormattedError {
    consequences?: string;
    countermeasures?: string;
    what: string;
    why: string;
}
