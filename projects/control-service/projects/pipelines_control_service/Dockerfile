# Dockerfile for a Spring Boot app based on
# https://spring.io/blog/2020/01/27/creating-docker-images-with-spring-boot-2-3-0-m1

# Builder stage
# This stage is implemented like in the guide, but it may be more efficient to
# have it in the gradle build process outside docker.
FROM eclipse-temurin:17 as builder
ARG JAR_NAME
WORKDIR application
COPY ./${JAR_NAME} application.jar
RUN java -Djarmode=layertools -jar application.jar extract


# Final stage
FROM eclipse-temurin:17
LABEL maintainer="Project Versatile Data Kit <miroslavi@vmware.com>"

# install kerberos client so that we can use kadmin
RUN apt-get -qq update && \
    apt-get -yqq --no-install-recommends install krb5-user

WORKDIR application
COPY --from=builder application/dependencies/ ./
COPY --from=builder application/spring-boot-loader/ ./
COPY --from=builder application/snapshot-dependencies/ ./
COPY --from=builder application/application/ ./

ENV SPRING_PROFILE=prod

ARG DATAJOBS_GIT_COMMIT_HASH
ENV DATAJOBS_GIT_COMMIT_HASH=$DATAJOBS_GIT_COMMIT_HASH

# Additional ways to control the application from outside.
# Remember that you can't pass as environment variables Spring properties that have . in the name.
ENV EXTRA_JAVA_OPTS=""
ENV EXTRA_ARGUMENTS=""

CMD java \
 -Dsun.security.krb5.debug=true \
 -Dspring.profiles.active=${SPRING_PROFILE} \
 ${EXTRA_JAVA_OPTS} \
 org.springframework.boot.loader.JarLauncher \
 ${EXTRA_ARGUMENTS}
