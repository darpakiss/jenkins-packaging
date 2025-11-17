ARG UBU_VERSION=jammy-20251013
# hadolint ignore=DL3006
FROM ubuntu:${UBU_VERSION}

SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install python3-pip python3-venv python-is-python3 sudo && \
    groupadd -g 1000 jenkins && useradd -u 1000 -g 1000 -m -s /bin/bash jenkins && \
    echo 'Defaults:jenkins !fqdn' > /etc/sudoers.d/jenkins && \
    echo 'Defaults:jenkins !requiretty' >> /etc/sudoers.d/jenkins && \
    echo 'jenkins ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers.d/jenkins && \
    apt-get clean && rm -rf /var/lib/apt/lists/*