#!/bin/bash

# shellcheck disable=SC1091
source /etc/os-release
export TZ='Europe/Amsterdam' && export DEBIAN_FRONTEND=noninteractive
rm -fr  /etc/apt/sources.list.d/backports.list 
apt-get update && apt-get dist-upgrade -y && apt-get install --no-install-recommends -y apt-utils tzdata && \
rm /etc/localtime && \
ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata && \
apt-get install --no-install-recommends -y vim procps telnet wget gpg ca-certificates git && \
wget --no-verbose -O - https://download.docker.com/linux/debian/gpg | gpg --dearmor --no-tty --batch --yes > /etc/apt/trusted.gpg.d/docker.gpg
echo "deb [arch=amd64] https://download.docker.com/linux/debian $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list && apt-get update
apt-get --no-install-recommends -y --allow-downgrades install docker-ce=5:28.5.2-1~debian.12~bookworm docker-ce-cli=5:28.5.2-1~debian.12~bookworm containerd.io docker-buildx-plugin docker-compose-plugin

apt-get clean && apt-get autoclean && rm -rf /var/lib/apt/lists/*

usermod -aG docker vagrant
echo -e "function docker-compose {\n  docker compose \"\$@\"\n}" > /etc/profile.d/docker-compose.sh
DOCKER_GROUP=$(getent group docker|cut -f3 -d":")
sed -i "s/^DOCKER_GROUP=.*/DOCKER_GROUP=${DOCKER_GROUP}/" /vagrant/.env

mkdir -pv /vagrant/jenkins-data /vagrant/jenkins-agent-data
chown -Rv 1000:1000 /vagrant/jenkins-data /vagrant/jenkins-agent-data

COMP_FILE="/vagrant/docker-compose.yaml"
if [ -f "$COMP_FILE" ];then
    if (docker compose -f "$COMP_FILE" config -q);then
        docker compose --progress=plain -f "$COMP_FILE" up -d --build --force-recreate
    else
        echo "ERROR : The '$COMP_FILE' is not ready to provision, please check the file and the related '.env' file!"
    fi
else
    echo "WARNING : '$COMP_FILE' does not exist, provisioning finished now."
fi
