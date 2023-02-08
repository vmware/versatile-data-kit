import { Pipe, PipeTransform } from '@angular/core';

import { VmwSimpleTranslateService } from './simple-translate.service';

@Pipe({
    name: 'simpleTranslate',
    pure: false,
})
export class VmwSimpleTranslatePipe implements PipeTransform {
    constructor(private simpleTranslate: VmwSimpleTranslateService) {}

    transform(text: string, ...args: any[]) {
        return this.simpleTranslate.translate(text, ...args);
    }
}
