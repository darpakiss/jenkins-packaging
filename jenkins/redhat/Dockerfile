ARG RH_VERSION=9.6.20250531
# hadolint ignore=DL3006
FROM rockylinux/rockylinux:${RH_VERSION}

SHELL ["/bin/bash", "-c"]

# yum install python3-virtualenv python3  --setopt tsflags=test
RUN yum makecache && \
    yum -y install python3-virtualenv python3 && \
    yum clean all && rm -rf /var/cache/yum && \
    update-alternatives --set python /usr/bin/python3


