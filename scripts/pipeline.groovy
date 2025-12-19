def buildApp() {
    if (isUnix()) {
        echo 'building the project...'
        sh "docker compose up --build"
    } else {
        echo 'building the project...'
        bat "docker compose up --build"
    }
}

def testApp() {
    echo 'testing the project...' // not actually testing right now
}

def deployApp() {
    echo 'deploying the project...' // not actually deploying yet
}

def postApp() {
    if (isUnix()) {
        sh "docker compose down"
    } else {
        bat "docker compose down"
    }
}

return this