

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
                    BRANCH_NAME == 'main'  //only executing if current branch is the main branch
                }
            }
            steps {
                echo 'testing the project...'
            }
        }
    }
}