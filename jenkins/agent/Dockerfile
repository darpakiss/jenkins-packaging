FROM jenkins/ssh-agent:latest-jdk21

SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND=noninteractive
ARG DOCK_URL="https://download.docker.com/linux/debian"
ARG DOCKER_VERSION="5:28.5.2-1~debian.13~trixie"
ARG DOCKER_GROUP="996"

RUN apt-get update && \
    apt-get install --no-install-recommends -y wget gpg ca-certificates xz-utils ruby rpm binutils \
    python3-pip python3-venv python-is-python3 && \
    source /etc/os-release && \
    wget --no-verbose -O - "${DOCK_URL}/gpg" | gpg --dearmor --no-tty --batch --yes > /etc/apt/trusted.gpg.d/docker.gpg && \
    echo "deb [arch=amd64] ${DOCK_URL} $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get --no-install-recommends -y --allow-downgrades install docker-ce-cli=${DOCKER_VERSION} && \
    groupadd -r -g ${DOCKER_GROUP} docker && usermod -aG docker jenkins && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

