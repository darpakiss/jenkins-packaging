FROM jenkins/ssh-agent:latest-jdk21

SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install wget xz-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

