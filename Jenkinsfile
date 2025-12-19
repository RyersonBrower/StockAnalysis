def gv

pipeline {
    agent any

    stages {
        stage ("init") {
            steps {
                script {
                    gv = load "script.groovy"
                }
            }
        }

        stage ("build") {
            steps {
                script {
                    gv.buildApp()
                }
            }
        }

        stage ("test") {
            steps {
                echo 'testing the project...'
                sh "docker compose up --abort-on-container-exit"
            }
        }
    }
    post {
        always {
            sh 'docker compose down'
        }
    }
}