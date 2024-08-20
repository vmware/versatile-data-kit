
The plugin provides GSSAPI Kerberos authentication on data job startup. The plugin also adds Kerberos/GSSAPI support for HTTP requests.

# Usage

To install the plugin, run:

```bash
pip install vdk-oauth-auth
```

## Configuration

The following environment variables can be used to configure this plugin:

| name                | description                                   |
|---------------------|-----------------------------------------------|
| `CLIENT_ID`         | Client id to fetch access token from CSP.     |
| `CLIENT_SECRET`     | Client secret to fetch access token from CSP. |
