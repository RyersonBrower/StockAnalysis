def buildApp() {
    echo 'building the project...'
    sh "docker compose build"
}

return this