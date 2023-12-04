FROM mcr.microsoft.com/playwright:v1.39.0-jammy

RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN DEBIAN_FRONTEND=noninteractive apt install python3.9 python3.9-venv -y
RUN apt-get install -y gcc python3.9-dev
