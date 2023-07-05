FROM cypress/browsers:node16.14.2-slim-chrome100-ff99-edge

RUN apt-get update && apt-get install -y \
    curl \
    zip \
    openjdk-11-jdk \
    git \
    openssl \
    bash

ENV NVM_VERSION=0.39.3
ENV NODE_VERSION=18.12.0
ENV NPM_VERSION=9.7.2
ENV ANGULAR_CLI_VERSION=13.3.11
ENV CYPRESS_VERSION=12.16.0

# Install nvm for managing nodejs and install nodejs
RUN curl -fsSL -o nvm-install.sh https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh
RUN mv ./nvm-install.sh /usr/local && mkdir /usr/local/.nvm

ENV NVM_DIR=/usr/local/.nvm

RUN chmod 700 /usr/local/nvm-install.sh && ./usr/local/nvm-install.sh
RUN chmod 777 /usr/local/.nvm/.cache
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}

ENV PATH="${NVM_DIR}/versions/node/v${NODE_VERSION}/bin/:${PATH}"
ENV HOME=/usr/local/.nvm/.cache
ENV CYPRESS_CACHE_FOLDER=/usr/local/.nvm/.cache

# Setup npm
RUN npm install -g npm@${NPM_VERSION}

# Install npm global dependencies and print engines version and global packages
RUN npm install -g @angular/cli@${ANGULAR_CLI_VERSION} cypress@${CYPRESS_VERSION} npm-cli-login && npm version && npm ls -g

# Install sonar scanner, requires java
RUN mkdir -p /opt; \
    curl -fSL https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472.zip -o /opt/sonar-scanner.zip; \
    unzip /opt/sonar-scanner.zip -d /opt; \
    rm /opt/sonar-scanner.zip; \
    ln -s /opt/sonar-scanner-4.6.2.2472/bin/sonar-scanner /usr/bin/sonar-scanner
