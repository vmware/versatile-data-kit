The plugin provides GSSAPI Kerberos authentication on data job startup. The plugin also adds Kerberos/GSSAPI support for HTTP requests.

# Usage

To install the plugin, run:

```bash
pip install vdk-kerberos-auth
```

The plugin dependency `requests-kerberos==0.12.0` may fail to install on Ubuntu with the following error:

```
  src/kerberosbasic.h:17:10: fatal error: gssapi/gssapi.h: No such file or directory
     17 | #include <gssapi/gssapi.h>
        |          ^~~~~~~~~~~~~~~~~
  compilation terminated.
```

If this is the case, install `libkrb5-dev` with the command below and try reinstalling the plugin:
```bash
sudo apt-get install -y libkrb5-dev
```

The following environment variables can be used to configure this plugin:

| name                    | description                                                                                                                                                    |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `VDK_KRB_AUTH`          | Specifies the Kerberos authentication type to use. Possible values are 'minikerberos' and 'kinit'. If left empty, the authentication is disabled.              |
| `VDK_KEYTAB_FILENAME`   | Specifies the name of the keytab file. If left empty, the name of the keytab file is assumed to be the same as the name of the data job with '.keytab' suffix. |
| `KEYTAB_FOLDER`         | Specifies the folder containing the keytab file. If left empty, the keytab file is expected to be located inside the data job folder.                          |
| `VDK_KEYTAB_PRINCIPAL`  | Specifies the Kerberos principal. If left empty, the principal will be the job name prepended with 'pa__view_'.                                                |
| `VDK_KEYTAB_REALM`      | Specifies the Kerberos realm. This value is used only with the 'minikerberos' authentication type. The default value is 'default_realm'.                       |
| `VDK_KERBEROS_KDC_HOST` | Specifies the name of the Kerberos KDC (Key Distribution Center) host. This value is used only with the 'minikerberos' authentication type.                    |
