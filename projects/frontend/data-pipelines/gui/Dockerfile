FROM nginxinc/nginx-unprivileged:stable-alpine
LABEL maintainer="Versatile Data Kit <join-versatiledatakit@groups.vmware.com>"

# Default (prod) nginx config file
ARG nginxConfig=nginx.conf

COPY ./config/${nginxConfig} /etc/nginx/conf.d/default.conf
COPY ./dist/ui /usr/share/nginx/html
