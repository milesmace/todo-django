pipeline {
    agent {
        docker {
            image 'docker:27-cli'
            args '--entrypoint="" -u root -v /var/run/docker.sock:/var/run/docker.sock -e HOME=/tmp'
        }
    }

    environment {
        DISCORD_WEBHOOK_URL = credentials('todo-discord-webhook')
    }

    stages {
        stage('Setup Container') {
            steps {
                sh 'apk add --no-cache curl'
            }
        }

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
                sh 'curl -X POST -H "Content-Type: application/json" -d \'{"content": "Tests passed"}\' $DISCORD_WEBHOOK_URL'
            }
        }

        stage('Clean workspace') {
            steps {
                cleanWs()
            }
        }
    }
}
