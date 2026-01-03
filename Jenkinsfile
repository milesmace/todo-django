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

        stage('Load env file') {
            steps {
                withCredentials([file(credentialsId: 'todo-django-env', variable: 'TEST_ENV_FILE')]) {
                    sh 'cp $TEST_ENV_FILE .env'
                }
            }
        }

        stage('Run tests') {
            steps {
                sh 'docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm web'
            }
        }
    }
}
