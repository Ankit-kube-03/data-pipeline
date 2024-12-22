
pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id') // AWS credentials in Jenkins
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key') // AWS secret key in Jenkins
        AWS_DEFAULT_REGION = 'us-west-1' // AWS region
        TERRAFORM_VERSION = '1.3.6' // Terraform version
        DOCKER_IMAGE_NAME = 'python-app' // Docker image name
        ECR_REPOSITORY = 'your-ecr-repository-url' // ECR repository URL
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Pull the latest code from the repository
                checkout scm
            }
        }

        stage('Terraform: Init') {
            steps {
                script {
                    sh '''
                        terraform init
                    '''
                }
            }
        }

        stage('Terraform: Plan') {
            steps {
                script {
                    sh '''
                        terraform plan -out=tfplan
                    '''
                }
            }
        }

        stage('Terraform: Apply') {
            steps {
                script {
                    sh '''
                        terraform apply -input=false tfplan
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                        docker build -t $DOCKER_IMAGE_NAME .
                    '''
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                        aws ecr get-login-password --region $AWS_DEFAULT_REGION | \
                        docker login --username AWS --password-stdin $ECR_REPOSITORY
                        
                        docker tag $DOCKER_IMAGE_NAME:latest $ECR_REPOSITORY:$BUILD_ID
                        docker push $ECR_REPOSITORY:$BUILD_ID
                    '''
                }
            }
        }

        stage('Deploy Lambda Function') {
            steps {
                script {
                    sh '''
                        aws lambda create-function \
                            --function-name python-lambda \
                            --package-type Image \
                            --code ImageUri=$ECR_REPOSITORY:$BUILD_ID \
                            --role arn:aws:iam::123456789012:role/lambda-role \
                            --timeout 900 \
                            --memory-size 512
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh '''
                        terraform destroy -auto-approve
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed!'
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }

        success {
            echo 'Pipeline executed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }
    }
}
