# Executed in a k8s environment and used to trigger a build for a data job image.
#
# To build the image:
# docker build -t taurus-builder -f k8s_vdk_job_builder/Dockerfile .
# To run the image locally:
# docker run -v /var/run/docker.sock:/var/run/docker.sock -e <ENV_VARIABLES> taurus-builder:latest <build_image.sh arguments>
FROM r.j3ss.co/img AS img
USER root

# Setup Python and Git
## Update & Install dependencies
RUN apk add --no-cache --update \
    git \
    bash \
    python3 py3-pip

# create symlink to img
RUN ln -s "$(which img)" "/usr/local/bin/docker"
RUN docker version

# AWS CLI
RUN pip3 install awscli  \
    && apk --purge -v del py3-pip \
    && rm -rf /var/cache/apk/*

# Copy builder script
COPY k8s_vdk_job_builder/build_image.sh /build_image.sh
RUN chmod +x /build_image.sh

# TODO:
# Download the latest vdk_job_builder python module from artifactory (pip repo) in build_image.sh
COPY cli.py /cli.py
COPY vdk_job_builder/ /vdk_job_builder

ENTRYPOINT ["/build_image.sh"]

# docker - Apache 2.0 https://docs.docker.com/engine/#licensing
# git - GPLv2 https://git-scm.com/about/free-and-open-source
# bash - GNU General Public License https://www.gnu.org/software/bash/
# python3 - PSF, Zero-Clause BSD https://docs.python.org/3/license.html
# pip - MIT https://github.com/pypa/pip/blob/main/LICENSE.txt
# awscli - Apache 2.0 https://github.com/aws/aws-cli/blob/develop/LICENSE.txt
