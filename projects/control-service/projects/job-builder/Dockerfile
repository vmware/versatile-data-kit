# Used to trigger a build for a data job image.

FROM gcr.io/kaniko-project/executor

FROM alpine

COPY --from=0 /kaniko /kaniko


ENV PATH $PATH:/kaniko
ENV SSL_CERT_DIR=/kaniko/ssl/certs
ENV DOCKER_CONFIG /kaniko/.docker/

WORKDIR /workspace

COPY Dockerfile.python.vdk /workspace/Dockerfile
COPY build_image.sh /build_image.sh
RUN chmod +x /build_image.sh


# Setup Python and Git
## Update & Install dependencies
RUN apk add --no-cache --update \
    git \
    bash

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.10/main python3=3.7.10-r0 py3-pip  \
    && pip3 install awscli  \
    && apk --purge -v del py3-pip \
    && rm -rf /var/cache/apk/*

ENTRYPOINT ["/build_image.sh"]
