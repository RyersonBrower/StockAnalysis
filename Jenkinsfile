def gv

pipeline {
    agent any

    environment {
        MYSQL_ROOT_PASSWORD = credentials('mysql-root-password-id')
        MYSQL_DATABASE = credentials('mysql-database-id')
        MYSQL_USER = credentials('mysql-user-id')
        MYSQL_PASSWORD = credentials('mysql-password-id')
    }

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