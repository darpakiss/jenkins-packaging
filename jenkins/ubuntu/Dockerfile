ARG UBU_VERSION=jammy-20251013
# hadolint ignore=DL3006
FROM ubuntu:${UBU_VERSION}

SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install python3-venv python3 python-is-python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*