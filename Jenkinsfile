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
                }
                sh '''
                  |mkdir -p $WORKSPACE/bin
                  |wget -q -O - https://github.com/koalaman/shellcheck/releases/download/stable/shellcheck-stable.linux.x86_64.tar.xz | \\
                  |tar --strip-components=1 -xJ shellcheck-stable/shellcheck -O > $WORKSPACE/bin/shellcheck
                  |chmod a+x $WORKSPACE/bin/*
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
        stage('Test Python app') {
            steps {
                sh '''
                  |for shellfile in $(find ./ -type f -name "*.sh");do
                  |  bash -n "$shellfile"
                  |  $WORKSPACE/bin/shellcheck "$shellfile"
                  |done
                '''.stripMargin('|')
            }
        }
        stage('Build packages') {
            parallel {
                stage('Ubuntu packaging') {
                    agent {
                        docker {
                            image 'ubuntu-buildenv:latest'
                            reuseNode true
                        }
                    }
                    stages{
                        stage('Build DEB package') {
                            steps {
                                sh '''
                                  |echo "Build"
                                '''.stripMargin('|')
                            }
                        }
                    }
                }
                stage('RedHat packaging') {
                    agent {
                        docker {
                            image 'redhat-buildenv:latest'
                            reuseNode true
                        }
                    }
                    stages{
                        stage('Build RPM package') {
                            steps {
                                sh '''
                                  |echo "Build"
                                '''.stripMargin('|')
                            }
                        }
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
                    stages{
                        stage('Test DEB package') {
                            steps {
                                sh '''
                                  |echo "Test"
                                '''.stripMargin('|')
                            }
                        }
                    }
                }
                stage('RedHat test') {
                    agent {
                        docker {
                            image 'redhat-buildenv:latest'
                            reuseNode true
                        }
                    }
                    stages{
                        stage('Test RPM package') {
                            steps {
                                sh '''
                                  |echo "Build"
                                '''.stripMargin('|')
                            }
                        }
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
            archiveArtifacts allowEmptyArchive: true, artifacts: 'base-version.txt,output/*.deb, output/*.rpm', followSymlinks: false
        }
    }
}
