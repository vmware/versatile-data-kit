# Secure Job Builder

Secure Job Builder extends [the standard job-builder ](../job-builder/README.md) and
provides a secure environment for the execution of data jobs in Python.

It uses a [secure base Python image](versatiledatakit/data-job-base-python-3.10-secure:latest),
creates a non-root user to perform tasks, remove execution permissions on data job files.
It also removes several system executables and pip, minimizing the attack surface within the container.
