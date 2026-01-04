pipeline {
    agent {
        docker {
            image 'docker:27-cli'
            args '--entrypoint="" -u root -v /var/run/docker.sock:/var/run/docker.sock -e HOME=/tmp'
        }
    }

    environment {
        DISCORD_WEBHOOK_URL = credentials('todo-discord-webhook')
        IMAGE_NAME = 'loginmail/todo-django'
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
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'todo-django-docker-creds',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $IMAGE_NAME:$BUILD_NUMBER .'
                sh 'docker tag $IMAGE_NAME:$BUILD_NUMBER $IMAGE_NAME:latest'
            }
        }

        stage('Docker Push') {
            steps {
                sh 'docker push $IMAGE_NAME:$BUILD_NUMBER'
                sh 'docker push $IMAGE_NAME:latest'
            }
        }
    }

    post {
        always {
            sh 'docker compose -f docker-compose.yml -f docker-compose.test.yml down -v'
        }
        failure {
            sh '''
            curl -X POST \
            -H "Content-Type: application/json" \
            -d '{"content": "Build failed. Image was not pushed."}' \
            $DISCORD_WEBHOOK_URL
            '''
        }
        success {
            sh '''
            curl -X POST \
            -H "Content-Type: application/json" \
            -d '{"content": "Build passed. Image pushed successfully to Docker Hub."}' \
            $DISCORD_WEBHOOK_URL
            '''
        }
        cleanup {
            sh 'docker logout'
            cleanWs()
        }
    }
}
