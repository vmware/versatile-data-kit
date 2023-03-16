/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { Injectable } from '@angular/core';

const DEFAULT_LANGUAGE = 'en';

@Injectable({
    providedIn: 'root'
})
export class VdkSimpleTranslateService {
    private language: string = DEFAULT_LANGUAGE;
    private translations: any = {};

    constructor() {
        const w: any = window as any;
        const language = w.navigator.language || w.navigator.userLanguage;
        this.setLanguage(language);
    }

    loadTranslationsForComponent(componentKey: string, translationsToAdd: any) {
        for (let language in translationsToAdd) {
            if (!this.translations[language]) {
                this.translations[language] = {};
            }

            for (let y in translationsToAdd[language]) {
                let newKey = componentKey + '.' + y;
                this.translations[language][newKey] = translationsToAdd[language][y];
            }
        }
    }

    setLanguage(language: string) {
        language = language.replace('-', '_');

        // check if different locale names are used for Simplified or Traditional Chinese
        const chineseMapping = {
            zh_Hans: 'zh_CN',
            zh_Hant: 'zh_TW'
        };
        language = chineseMapping[language] || language;

        // Special-case Chinese because we support both TW and CN locales
        // Also if the locale is pt_PT(Portuguese Portugal) we should default to EN
        // otherwise the 2 character language ID is what we want
        const mainLocale = language.substring(0, 2);
        const isChinese = language.length > 2 && mainLocale === 'zh';
        const isNotSupportedPortuguese = language.length > 2 && mainLocale === 'pt' && language !== 'pt_BR';

        if (isChinese || isNotSupportedPortuguese) {
            this.language = language;
        } else {
            this.language = mainLocale;
        }
    }

    getLanguage() {
        return this.language;
    }

    translate(key: any, ...args: any[]) {
        let translations = this.translations[this.language];

        //if there are no translations of the user's language set translations to equal the default language
        if (!translations) {
            translations = this.translations[DEFAULT_LANGUAGE] ? this.translations[DEFAULT_LANGUAGE] : [];
        }

        //if there is a translation get that translation otherwise use the default language
        let translation = undefined;
        if (translations[key]) {
            translation = translations[key];
        } else if (this.translations[DEFAULT_LANGUAGE]) {
            translation = this.translations[DEFAULT_LANGUAGE][key];
        }

        //if no translation is found in the user's language or in the default language then show an error string
        if (!translation) {
            translation = `!! Key ${key} not found !!`;
        }

        return this.format(translation, ...args);
    }

    private format(format: string, ...args: string[]) {
        return format.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    }
}
