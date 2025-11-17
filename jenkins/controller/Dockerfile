# Use quickstart-tutorials Jenkins controller image as base
# This image is maintained at https://github.com/jenkins-docs/quickstart-tutorials
# and published to GHCR automatically (twice daily)
FROM ghcr.io/jenkins-docs/quickstart-tutorials/jenkinsci-tutorials:simple_controller_

# Switch to root for customizations
USER root

# Project-specific jobs (Poor man's JCasC)
COPY --chown=jenkins:jenkins ./Build-Configurator /usr/share/jenkins/ref/jobs/Build-Configurator
COPY --chown=jenkins:jenkins ./plugins.txt /opt

# SSH known_hosts setup for SSH agent connections
# Required to avoid: [SSH] No Known Hosts file was found at /var/jenkins_home/.ssh/known_hosts
RUN mkdir -p /var/jenkins_home/.ssh/ && \
    touch /var/jenkins_home/.ssh/known_hosts && \
    chown -R jenkins:jenkins /var/jenkins_home/.ssh/ && \
    java -jar /opt/jenkins-plugin-manager.jar --plugin-file /opt/plugins.txt --verbose

# Switch back to jenkins user
USER jenkins
