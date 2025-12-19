def buildApp() {
    if (isUnix()) {
        echo 'building the project...'
        sh "docker compose build"
    } else {
        echo 'building the project...'
        bat "docker compose build"
    }
}

return this