# Used to trigger a build for a data job image.
FROM moby/buildkit:v0.9.3-rootless

# Build-time configurable arguments for UID and user group
ARG UID=1000
ARG GID=1000

USER root

RUN mkdir /run/buildkit
RUN chown -R $UID:$GID /run/buildkit

COPY --chown=$UID:$GID Dockerfile.python.vdk /home/user/Dockerfile
COPY --chown=$UID:$GID build_image.sh /build_image.sh

RUN chmod +x /build_image.sh

# Setup Python and Git
## Update & Install dependencies
RUN apk add --no-cache --update \
    git \
    bash

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.10/main python3=3.7.10-r0 py3-pip \
    && pip3 install -U pip \
    && pip3 install awscli  \
    && apk --purge -v del py3-pip \
    && rm -rf /var/cache/apk/*

ENV BUILDKITD_FLAGS=--oci-worker-no-process-sandbox

USER user
WORKDIR /home/user

ENTRYPOINT ["/build_image.sh"]
