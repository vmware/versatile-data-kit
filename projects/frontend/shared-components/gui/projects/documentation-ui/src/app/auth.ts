import { AuthConfig } from 'angular-oauth2-oidc';

export const authCodeFlowConfig: AuthConfig = {
    issuer: 'https://console-stg.cloud.vmware.com/csp/gateway/am/api/',
    redirectUri: window.location.origin + '/index.html',
    skipIssuerCheck: true,
    requestAccessToken: true,
    oidc: true,
    strictDiscoveryDocumentValidation: false,
    clientId: 'Lt44bhN5yMowdEHuxO3v1SBDKsS3aXW4GcJ',
    responseType: 'code',
    scope: 'openid ALL_PERMISSIONS customer_number group_names',
    showDebugInformation: true,
    silentRefreshRedirectUri: window.location.origin + '/silent-refresh.html',
    useSilentRefresh: true, // Needed for Code Flow to suggest using iframe-based refreshes
    silentRefreshTimeout: 5000, // For faster testing
    timeoutFactor: 0.25, // For faster testing
    sessionChecksEnabled: true,
    clearHashAfterLogin: false, // https://github.com/manfredsteyer/angular-oauth2-oidc/issues/457#issuecomment-431807040,
    nonceStateSeparator: 'semicolon' // Real semicolon gets mangled by IdentityServer's URI encoding
};
