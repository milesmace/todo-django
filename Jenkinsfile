pipeline {
    agent {
        docker { image 'docker:27-cli' }
    }

    stages {
        stage('Clean workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }
    }
}
