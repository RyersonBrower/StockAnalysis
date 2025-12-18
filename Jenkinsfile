

pipeline {

    agent any

    stages {

        stage ("build") {
            steps {
                echo 'building the project...'
            }
        }

        stage ("test") {
            when {
                expression {
                    BRANCH_NAME == 'dev'  //only executing if current branch is the dev branch
                }
            }
            steps {
                echo 'testing the project...'
            }
        }
    }
}