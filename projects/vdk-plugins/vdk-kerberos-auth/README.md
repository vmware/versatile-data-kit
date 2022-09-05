The plugin provides GSSAPI Kerberos authentication on data job startup. The plugin also adds Kerberos/GSSAPI support for HTTP requests.

# Usage

To install the plugin, run:

```bash
pip install vdk-kerberos-auth
```

After it's install what happens:

1. Upon installation and if KEYTAB_FILENAME and KEYTAB_PRINCIPAL are configured, it will try to authenticate ("kinit") at the start of very VDK command.
2. Then when a client needs to talk to kerberos provision server they would use KerberosClient class to generate header:
With requests library, you'd use https://pypi.org/pypi/requests-kerberos.
The following can be used if another http library does not support kerberos to generate Authorization header:
```python
auth = KebrerosClient("http@server.fqdn.com")
headers['Authorization'] =  auth.read_kerberos_auth_header()
```

## Known issues

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

## Configuration

The following environment variables can be used to configure this plugin:

| name                    | description                                                                                                                                                    |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `KRB_AUTH`          | Specifies the Kerberos authentication type to use. Possible values are 'minikerberos' and 'kinit'. If left empty, the authentication is disabled.              |
| `KEYTAB_FILENAME`   | Specifies the name of the keytab file. If left empty, the name of the keytab file is assumed to be the same as the name of the data job with '.keytab' suffix. |
| `KEYTAB_FOLDER`         | Specifies the folder containing the keytab file. If left empty, the keytab file is expected to be located inside the data job folder.                          |
| `KEYTAB_PRINCIPAL`  | Specifies the Kerberos principal. If left empty, the principal will be the job name prepended with 'pa__view_'.                                                |
| `KEYTAB_REALM`      | Specifies the Kerberos realm. This value is used only with the 'minikerberos' authentication type. The default value is 'default_realm'.                       |
| `KERBEROS_KDC_HOST` | Specifies the name of the Kerberos KDC (Key Distribution Center) host. This value is used only with the 'minikerberos' authentication type.                    |


# Testing

In order to run the tests you need pytest and docker and kerberos client (kadmin).

You can use helper script `../build-plugin.sh` to build and test locally.

On Mac OS kadmin may miss some options needed. In this case you can use kadmin in docker to run the tests
```bash
export VDK_TEST_USE_KADMIN_DOCKER=true
cd /source/projects/vdk-plugins/vdk-kerberos-auth
../build-plugin.sh
```
