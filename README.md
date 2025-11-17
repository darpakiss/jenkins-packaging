# NIDS-Configurator

`nids-configurator` is a command-line configuration tool for a Network Intrusion Detection System (NIDS).  
It does **not** run or manage the NIDS engine itself – it only helps you **create and maintain a YAML config file**.

The tool is designed to work on:

- Ubuntu 22.04 LTS
- Red Hat Enterprise Linux 9.6

and is installed via a `.deb` package with the main components:

- `/usr/bin/nids-configurator` – user-facing CLI wrapper
- `/etc/default/nids-configurator` – default environment/configuration for the tool
- `/opt/nids-configurator/nids-configurator` – main Python application module

## What it configures

The configurator guides you through an interactive wizard to set:

- **General**
    - NIDS name
    - Config version
    - Enabled/disabled by default
- **Network**
    - Monitored interfaces
    - IPv4 home networks and excluded networks
    - IPv6 home networks and excluded networks
- **Rules**
    - Rule directory paths
    - Enabled / disabled rule sets
- **Logging**
    - Log mode: `file`, `syslog`, or `both`
    - Log file path
    - Syslog target (`host:port`)
    - Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

The result is a YAML configuration file suitable for use by a NIDS engine (e.g. Suricata/Snort or a custom NIDS).

## How it works

The application:

1. Detects the underlying OS family (Ubuntu / RHEL / other).
2. Loads built-in default values.
3. Optionally applies overrides from:
    - **Environment variables** (e.g. `NDIS_NIDS_NAME`, `NDIS_INTERFACES`, etc.)
    - **Command-line arguments**
4. Starts an interactive wizard where each question shows the current value as a default.
5. Writes the final configuration to a YAML file (typically `/etc/nids/nids-config.yml`).

This design allows you to:

- Preseed configuration via automation (env vars or CLI flags)
- Fine-tune or review settings interactively
- Keep the NIDS engine decoupled from the configuration logic

# Jenkins Vagrant Lab
This project lives in the `jenkins/` directory and provisions a Debian 12 Vagrant box running Jenkins.
Vagrant brings up a single VM, installs Docker, and starts a `docker-compose` project that runs Jenkins in a container.
Inside the VM, Jenkins builds and runs two Docker images: one based on Ubuntu and one based on Rocky Linux.
The Jenkins pipeline is fully scripted (declarative), covering checkout, build, test, and cleanup stages.

Each Linux distribution container is used solely to run integration tests implemented with TestInfra.
All Jenkins configuration (jobs, pipeline, plugins) is automated via provisioning scripts and configuration as code.
You can trigger the pipeline from the Jenkins UI to run the full test flow.
This setup is ideal for experimenting with Jenkins, Docker, and multi-platform CI on a disposable local lab.
The overall idea was inspired by [github.com/gounthar/MyFirstAndroidAppBuiltByJenkins](https://github.com/gounthar/MyFirstAndroidAppBuiltByJenkins.git).
