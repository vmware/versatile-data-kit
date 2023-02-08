export const FORWARD_SLASH = '/';

export const TIE_SWAGGER_DOC_LOCATION = 'swagger-ui.html#';

export class UrlUtil {
    static normalizeEndpoint(endPoint: string): string {
        if (!endPoint) {
            return '';
        }

        if (endPoint.endsWith(FORWARD_SLASH)) {
            return endPoint;
        }

        return endPoint + FORWARD_SLASH;
    }

    static constructTieSwaggerUiEndpoint(endpointBasePath: string) {
        return UrlUtil.normalizeEndpoint(endpointBasePath) + TIE_SWAGGER_DOC_LOCATION;
    }
}
