pipeline {
    agent any
    environment {
        IMAGE_NAME = 'toph2490/my_to_do_list'
        VERSION = "${BUILD_NUMBER}"
        email = 'toph2913@gmail.com'
        REMOTE_USER = 'ubuntu'
        REMOTE_HOST_STAGE = '172.31.33.207'
        REMOTE_HOST_PRODUCTION = '172.31.43.125'
        DB_HOST = '172.31.38.238'
    }
    stages {
        stage('Build Docker Image') {
            when { not {branch 'main'} }
            steps {
                sh '''
                    docker build -t myapp ./app
                    docker tag myapp ${IMAGE_NAME}:${VERSION}
                    docker tag myapp ${IMAGE_NAME}:latest
                '''
            }
        }
        stage('Run app with Docker compose') {
            when { not {branch 'main'} }
            steps {
                sh '''
                    docker compose down || true
                    docker compose up -d
                '''
            }
        }
        stage('Run Tests') {
            when { not {branch 'main'} }
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r tests/requirements.txt
                    pytest ./tests
                '''
            }
        }
        stage('Push Docker Image') {
            when { not {branch 'main'} }
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    script {
                        docker.withRegistry('', 'docker-hub') {
                            docker.image("${IMAGE_NAME}").push("${VERSION}")
                            docker.image("${IMAGE_NAME}").push('latest')    
                        }
                    }
                   }
                }
            }
        stage('Deploy to staging') {
            when { not {branch 'main'} }
            steps {
                    withCredentials([usernamePassword(credentialsId: 'DB_PASS', passwordVariable: 'DB_PASSWORD', usernameVariable: 'DB_USERNAME')]) {
                    sshagent (credentials: ['node1']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST_STAGE} \
                            "docker pull ${IMAGE_NAME}:${VERSION} && docker rm -f myapp && \
                            docker run -d --name myapp --restart unless-stopped \
                            -e DB_NAME=todo -e DB_USER=${DB_USERNAME} -e DB_PASSWORD=${DB_PASSWORD} -e DB_HOST=${DB_HOST} \
                            -p 5000:5000 ${IMAGE_NAME}:${VERSION}"
                         """
                }
            }
            }    
        }
        stage('Create PR to main') {
            when { not {branch 'main'} }
            steps {
                withCredentials([string(credentialsId: 'github', variable: 'GH_TOKEN')]) {
                    script {
                        def prTitle = "Merge ${BRANCH_NAME} into main @${VERSION}"
                        def prBody = "This PR merges changes from ${BRANCH_NAME} into main. http://stage.yp3yp3.online/"
                        def prUrl = "https://api.github.com/repos/yp3yp3/Todo_list/pulls"
                        sh """
                            curl -X POST \
                            -H "Authorization: token ${GH_TOKEN}" \
                            -H "Accept: application/vnd.github.v3+json" \
                            -d '{ \
                            \"title\": \"${prTitle}\", \
                            \"head\": \"${BRANCH_NAME}\", \
                            \"base\": \"main\", \
                            \"body\": \"${prBody}\" \
                            }' \
                            ${prUrl}
                        """
                    }
                }
            }
        }
        stage('deploy to production') {
            when { branch 'main' }
            steps {
                       // Extract version number from the latest Git commit message
                script {
                    def version = sh(
                        script: "git log -1 --pretty=%B | grep -oE '@[0-9]+' | tr -d '@'",
                        returnStdout: true
                    ).trim()

                    if (!version) {
                        error("❌ ERROR: No version number found in commit message. Make sure it includes @<number>.")
                    }

                    env.NEW_VERSION = version
                    echo "📦 Extracted version from commit: ${env.NEW_VERSION}"
                }

                withCredentials([usernamePassword(credentialsId: 'DB_PASS', passwordVariable: 'DB_PASSWORD', usernameVariable: 'DB_USERNAME')]) {
                    sshagent (credentials: ['node1']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST_PRODUCTION} \
                            "docker pull ${IMAGE_NAME}:${NEW_VERSION} && docker rm -f myapp && \
                            docker run -d --name myapp --restart unless-stopped \
                            -e DB_NAME=todo -e DB_USER=${DB_USERNAME} -e DB_PASSWORD=${DB_PASSWORD} -e DB_HOST=${DB_HOST} \
                            -p 5000:5000 ${IMAGE_NAME}:${NEW_VERSION}"
                         """
                }
            }
        }
    }
    }
        post {
             failure {
                slackSend(
                    channel: '#jenkins',
                    color: 'danger',
                    message: "${JOB_NAME}.${BUILD_NUMBER} FAILED"
                )
                
                emailext(
                    subject: "${JOB_NAME}.${BUILD_NUMBER} FAILED",
                    mimeType: 'text/html',
                    to: "$email",
                    body: "${JOB_NAME}.${BUILD_NUMBER} FAILED"
                )
            }
            success {
                slackSend(
                    channel: '#jenkins',
                    color: 'good',
                    message: "${JOB_NAME}.${BUILD_NUMBER} PASSED http://stage.yp3yp3.online/"
                )
                emailext(
                    subject: "${JOB_NAME}.${BUILD_NUMBER} PASSED",
                    mimeType: 'text/html',
                    to: "$email",
                    body: "${JOB_NAME}.${BUILD_NUMBER} PASSED"
                )
            }
            always {
                sh '''
                    docker compose down || true
                    docker rmi myapp || true
                '''
            }
        }
    }