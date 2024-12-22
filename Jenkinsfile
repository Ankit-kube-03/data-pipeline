pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1' // Update to match your Terraform setup
        ECR_REPO_URL = "804425018582.dkr.ecr.us-east-1.amazonaws.com/data-pipeline-app" // Replace with actual URL
        DOCKER_IMAGE_NAME = 'data-pipeline-app:latest'
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Fetch source code from the repository
                git branch: 'main', url: 'https://github.com/Ankit-kube-03/data-pipeline.git' // Update with actual repo URL
            }
        }

        stage('Terraform Init & Apply') {
            steps {
                script {
                    sh '''
                        terraform init
                        terraform apply -auto-approve
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker build -t ${DOCKER_IMAGE_NAME} .
                        docker run -d --name mypipeline ${DOCKER_IMAGE_NAME} 
                    '''
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URL}
                        docker tag ${DOCKER_IMAGE_NAME} ${ECR_REPO_URL}:${BUILD_NUMBER}
                        docker push ${ECR_REPO_URL}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Update Lambda Function') {
            steps {
                script {
                    sh '''
                        aws lambda update-function-code \
                            --function-name data-pipeline-function \
                            --image-uri ${ECR_REPO_URL}:${BUILD_NUMBER}
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully.'
        }
        failure {
            echo 'Pipeline execution failed.'
        }
    }
}





