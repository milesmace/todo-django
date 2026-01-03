pipeline {
    agent {
        docker {
            image 'docker:27-cli'
            args '--entrypoint="" -u root -v /var/run/docker.sock:/var/run/docker.sock -e HOME=/tmp'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Load env') {
            steps {
                withCredentials([
                    file(credentialsId: 'todo-django-env', variable: 'TEST_ENV_FILE')
                ]) {
                    sh 'cp $TEST_ENV_FILE .env'
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm web'
            }
        }

        stage('Clean workspace') {
            steps {
                cleanWs()
            }
        }
    }
}
