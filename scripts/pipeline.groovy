def buildApp() {
    echo 'building the project...'
    if (isUnix()) {
        sh "docker compose up -d --build"
    } else {    
        bat "docker compose up -d --build"
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