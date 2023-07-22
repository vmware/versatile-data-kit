# Used to trigger a build for a data job image.

FROM gcr.io/kaniko-project/executor:debug

WORKDIR /workspace

COPY Dockerfile.python.vdk /workspace/Dockerfile
COPY build_image.sh /build_image.sh
RUN chmod +x /build_image.sh

ENTRYPOINT ["/build_image.sh"]
