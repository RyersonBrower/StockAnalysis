def gv

pipeline {
    agent any

    stages {
        stage ("init") {
            steps {
                script {
                    gv = load "scripts/pipeline.groovy"
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
                script {
                    gv.testApp()
                }
            }
        }

        stage ("deploy") {
            steps {
                script {
                    gv.deployApp()
                }
            }
        }
    }
    post {
        always {
            script {
                gv.postApp()
            }
        }
    }
}