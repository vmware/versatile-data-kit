import { TestBed, inject } from "@angular/core/testing";

import { VmwSimpleTranslateService } from "./simple-translate.service";

const mockTranslations = {
    'en': {
        'chat-with-vmware-support': 'Chat with VMware Support',
        'return-to-chat': "Return to chat"
    },
    'es': {
        'chat-with-vmware-support': 'Conversa con VMware Support',
        'return-to-chat': "Retornar a conversacion"
    }
};

describe("VmwSimpleTranslateService", () => {
    let service: VmwSimpleTranslateService;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                VmwSimpleTranslateService
            ]
        });

        service = TestBed.inject(VmwSimpleTranslateService);
    });

    it("should accept a LCID and set language", () => {
        expect(service).toBeTruthy();
        expect(service.getLanguage()).toEqual('en');
        service.setLanguage('es-CO');
        expect(service.getLanguage()).toEqual('es');
        service.setLanguage('es_CO');
        expect(service.getLanguage()).toEqual('es');
        service.setLanguage('zh_TW');
        expect(service.getLanguage()).toEqual('zh_TW');
        service.setLanguage('zh');
        expect(service.getLanguage()).toEqual('zh');
    });

    it("should translate string as per specified language", () => {
        service.setLanguage('es-CO');

        service.loadTranslationsForComponent('test', mockTranslations);

        expect(service.translate('test.return-to-chat')).toEqual('Retornar a conversacion');
    });

    it("should return translation in the default langauge if the string does not exist in the specified language", () => {
        service.setLanguage('pl-PL');

        service.loadTranslationsForComponent('test', mockTranslations);

        expect(service.translate('test.return-to-chat')).toEqual('Return to chat');
    });

    it("error message should show if key is not found", () => {
        service.setLanguage('pl-PL');

        service.loadTranslationsForComponent('test', mockTranslations);

        expect(service.translate('test.some-non-existing-key')).toEqual('!! Key test.some-non-existing-key not found !!');
    });
});
