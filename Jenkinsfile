def sendDiscordNotification(boolean isSuccess) {
    sh 'git config --global --add safe.directory "$WORKSPACE"'

    def duration = currentBuild.durationString.replace(' and counting', '')
    def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    def commitMessage = sh(script: 'git log -1 --pretty=%s', returnStdout: true).trim()
    def commitAuthor = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
    def branchName = env.GIT_BRANCH ?: sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()

    def title = isSuccess ? "✅ Build Successful" : "❌ Build Failed"
    def description = isSuccess
        ? "The build passed and the Docker image was **pushed successfully**!"
        : "The build failed and the Docker image was **not pushed**."
    def color = isSuccess ? 3066993 : 15158332

    def dockerFields = isSuccess ? """
                            {"name": "🐳 Image", "value": "`${env.IMAGE_NAME}:${env.BUILD_NUMBER}`", "inline": true},
                            {"name": "🐳 Docker Hub", "value": "[View Image](https://hub.docker.com/r/${env.IMAGE_NAME}/tags)", "inline": true},""" : ""

    def payload = """{
        "embeds": [{
            "title": "${title}",
            "description": "${description}",
            "color": ${color},
            "fields": [
                {"name": "📦 Job", "value": "${env.JOB_NAME}", "inline": true},
                {"name": "🔢 Build", "value": "#${env.BUILD_NUMBER}", "inline": true},
                {"name": "⏱️ Duration", "value": "${duration}", "inline": true},
                {"name": "🌿 Branch", "value": "${branchName}", "inline": true},
                {"name": "👤 Author", "value": "${commitAuthor}", "inline": true},
                {"name": "🔗 Commit", "value": "`${commitHash}`", "inline": true},
                {"name": "💬 Message", "value": "${commitMessage}", "inline": false},${dockerFields}
                {"name": "🔗 Links", "value": "[Build](${env.BUILD_URL}) | [Console](${env.BUILD_URL}console)", "inline": false}
            ],
            "timestamp": "${new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'", TimeZone.getTimeZone('UTC'))}",
            "footer": {"text": "Jenkins CI/CD"},
            "url": "${env.BUILD_URL}"
        }]
    }"""

    sh """
    curl -X POST \
    -H "Content-Type: application/json" \
    -d '${payload}' \
    \$DISCORD_WEBHOOK_URL
    """
}

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
                sh 'docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm --build web'
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'todo-django-docker-creds',
                    usernameVariable: 'DOCKER_USERNAME',
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
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
            script {
                sendDiscordNotification(false)
            }
        }
        success {
            script {
                sendDiscordNotification(true)
            }
        }
        cleanup {
            sh 'docker logout'
            cleanWs()
        }
    }
}
