def EXECUTOR_LABEL = 'docker'

pipeline {
    parameters {
        booleanParam(name: 'DryRun', defaultValue: false, description: 'Set this TRUE when you want to just test the pipeline')
        gitParameter(type: 'PT_BRANCH', name: 'BRANCH', branchFilter: 'origin/(.*)', defaultValue: 'main',
                description: 'Choose a branch to checkout', selectedValue: 'DEFAULT', sortMode: 'DESCENDING_SMART')
    }
    options {
        skipStagesAfterUnstable()
        skipDefaultCheckout()
        timeout(time: 120, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
    }
    environment {
        DEBIAN_VERSION = '13'
        PKG = 'nids-configurator'
        DESC = 'NIDS Configurator'
        MAINTAINER = 'John Doe <johndoe@non-gmail.net>'
        VENDOR = 'ACME Corp'
        HPAGE = 'https://github.com/darpakiss/jenkins-packaging.git'
    }
    agent { label EXECUTOR_LABEL }
    stages {
        stage('Prepare build') {
            steps {
                cleanWs()
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(script: "set -x ; git rev-parse --short HEAD", returnStdout: true).trim()
                    env.GIT_COMMIT = sh(script: "set -x ; git rev-parse HEAD", returnStdout: true).trim()
                    env.TIMESTAMP = sh(script: "date '+%Y%m%d-%H%M%S'", returnStdout: true).trim()
                }
                sh '''
                  |mkdir -p $WORKSPACE/bin
                  |wget -q -O - https://github.com/koalaman/shellcheck/releases/download/stable/shellcheck-stable.linux.x86_64.tar.xz | \\
                  |tar --strip-components=1 -xJ shellcheck-stable/shellcheck -O > $WORKSPACE/bin/shellcheck
                  |chmod a+x $WORKSPACE/bin/*
                  |gem install fpm
                  |pip install flake8 --user --break-system-packages
                  |mkdir output
                '''.stripMargin('|')
            }
        }
        stage('Check shell scripts') {
            steps {
                sh '''
                  |for shellfile in $(find ./ -type f -name "*.sh");do
                  |  bash -n "$shellfile"
                  |  $WORKSPACE/bin/shellcheck "$shellfile"
                  |done
                '''.stripMargin('|')
            }
        }
        stage('Check Python Flake8') {
            steps {
                sh '''
                  |export PATH="$HOME/.local/bin:$PATH"
                  |for pyfile in $(find ./ -type f -name "*.py");do
                  |  flake8 --verbose "$pyfile"
                  |done
                '''.stripMargin('|')
            }
        }
        stage('Unit Testing Python') {
            steps {
                sh '''
                  |mkdir -p test-reports
                  |python3 -mvenv ./venv
                  |. ./venv/bin/activate
                  |pip install -r requirements-unittest.txt
                  |env PYTHONPATH=src/ pytest tests/test* --junit-xml=test-reports/pytest-result.xml \\
                  |--cov-report term:skip-covered
                '''.stripMargin('|')
            }
        }

        stage('Build packages') {
            parallel {
                stage('Ubuntu packaging') {
                    steps {
                        sh '''
                            |echo "Build"
                            |PATH="$(ruby -e 'puts Gem.user_dir')/bin:$PATH"
                            |mkdir -p deb_pkg/usr/bin/ deb_pkg/etc/default/ deb_pkg/opt/$PKG
                            |cp -v wrapper/$PKG deb_pkg/usr/bin/
                            |cp -v wrapper/default deb_pkg/etc/default/$PKG
                            |cp -av src/nids_configurator deb_pkg/opt/$PKG
                            |fpm -s dir -t deb --name "$PKG" --version "$TIMESTAMP" --description "$DESC" \\
                            |--maintainer "$MAINTAINER" --url "$HPAGE" --vendor "$VENDOR" --category "admin" \\
                            |--chdir deb_pkg -d python3 -d python3-yaml
                            |mv -v nids-configurator*_amd64.deb output/
                        '''.stripMargin('|')
                    }
                }
                stage('RedHat packaging') {
                    steps {
                        sh '''
                            |echo "Build"
                            |PATH="$(ruby -e 'puts Gem.user_dir')/bin:$PATH"
                            |mkdir -p rpm_pkg/usr/bin/ rpm_pkg/etc/default/ rpm_pkg/opt/$PKG
                            |cp -v wrapper/$PKG rpm_pkg/usr/bin/
                            |cp -v wrapper/default rpm_pkg/etc/default/$PKG
                            |cp -av src/nids_configurator rpm_pkg/opt/$PKG
                            |fpm -s dir -t rpm --name "$PKG" --version "$TIMESTAMP" --description "$DESC" \\
                            |--maintainer "$MAINTAINER" --url "$HPAGE" --vendor "$VENDOR" --category "admin" \\
                            |--chdir deb_pkg -d python3 -d python3-pyyaml
                            |mv -v nids-configurator*.x86_64.rpm output/
                        '''.stripMargin('|')
                    }
                }
            }
        }
        stage('Test packages') {
            parallel {
                stage('Ubuntu Test') {
                    agent {
                        docker {
                            image 'ubuntu-buildenv:latest'
                            reuseNode true
                        }
                    }
                    steps {
                        sh '''
                          |export DEBIAN_FRONTEND=noninteractive
                          |apt-get update
                          |apt-get install output/nids-configurator*_amd64.deb -y
                          |python3 -mvenv ./deb_venv
                          |. ./deb_venv/bin/activate
                          |pip install -r requirements-integration.txt
                          |py.test -v deploy_test/test_package_install.py
                        '''.stripMargin('|')
                    }
                }
                stage('RedHat test') {
                    agent {
                        docker {
                            image 'redhat-buildenv:latest'
                            reuseNode true
                        }
                    }
                    steps {
                        sh '''
                          |echo "Build"
                        '''.stripMargin('|')
                    }
                }
            }
        }
    }
    post {
        success {
            sh '''
              | echo "$TIMESTAMP" > base-version.txt
            '''.stripMargin('|')
        }
        always {
            junit allowEmptyResults: true, testResults: 'test-reports/*.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'base-version.txt,output/*.deb, output/*.rpm', followSymlinks: false
        }
    }
}
