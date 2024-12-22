pipeline {
    agent any

    environment {
        #AWS_ACCESS_KEY_ID = credentials('aws-access-key-id') // Add AWS credentials in Jenkins
        #AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key') // Add AWS secret key in Jenkins
        AWS_DEFAULT_REGION = 'us-west-1' // Choose your AWS region
        TERRAFORM_VERSION = '1.3.6' // Specify your terraform version
        DOCKER_IMAGE_NAME = 'python-app' // Docker image name
        ECR_REPOSITORY = 'your-ecr-repository-url' // ECR repository URL
    }

    stages {
        stage('Checkout Code') {
            steps {
                node('master') {
                    script {
                        // Pull the latest code from the repository
                        checkout scm
                    }
                }
            }
        }

        stage('Terraform: Init') {
            steps {
                node('master') {
                    script {
                        // Initialize Terraform
                        sh 'terraform init'
                    }
                }
            }
        }

        stage('Terraform: Plan') {
            steps {
                node('master') {
                    script {
                        // Run Terraform plan
                        sh 'terraform plan -out=tfplan'
                    }
                }
            }
        }

        stage('Terraform: Apply') {
            steps {
                node('master') {
                    script {
                        // Apply the Terraform plan
                        sh 'terraform apply tfplan'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                node('master') {
                    script {
                        // Build the Docker image from the Dockerfile
                        sh 'docker build -t $DOCKER_IMAGE_NAME .'
                    }
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                node('master') {
                    script {
                        // Login to AWS ECR
                        sh '''aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY'''

                        // Tag the Docker image
                        sh '''docker tag $DOCKER_IMAGE_NAME:latest $ECR_REPOSITORY:$BUILD_ID'''

                        // Push Docker image to ECR
                        sh '''docker push $ECR_REPOSITORY:$BUILD_ID'''
                    }
                }
            }
        }

        stage('Deploy Lambda Function') {
            steps {
                node('master') {
                    script {
                        // Deploy Lambda function using the Docker image in ECR
                        sh '''aws lambda create-function \
                            --function-name python-lambda \
                            --package-type Image \
                            --code ImageUri=$ECR_REPOSITORY:$BUILD_ID \
                            --role arn:aws:iam::123456789012:role/lambda-role \
                            --timeout 900 --memory-size 512'''
                    }
                }
            }
        }

        stage('Cleanup') {
            steps {
                node('master') {
                    script {
                        // Clean up resources after the deployment
                        sh 'terraform destroy -auto-approve'
                    }
                }
            }
        }
    }

    post {
        always {
            // Archive Terraform logs and Docker build logs
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }

        success {
            // Notify successful pipeline execution (e.g., Slack, email)
            echo 'Pipeline executed successfully!'
        }

        failure {
            // Notify failure in the pipeline (e.g., Slack, email)
            echo 'Pipeline failed!'
        }
    }
}
