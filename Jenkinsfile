pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')  // Jenkins credential for AWS Access Key
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')  // Jenkins credential for AWS Secret Access Key
        AWS_REGION = 'us-east-1'  // Set your AWS region
        ECR_REPOSITORY = 'data-pipeline-app'  // ECR repository name
        LAMBDA_FUNCTION_NAME = 'data-pipeline-function'  // Lambda function name
        AWS_ACCOUNT_ID = '804425018582'  // Your AWS account ID
    }
    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Ankit-kube-03/data-pipeline.git'  // Replace with your GitHub repository URL
                branch 'main'
            }
        }
        stage('Build Docker Image') {
             steps {
                 dir('data-pipeline/Dockerfile') {
                     script {
                          node{
                          // Build Docker image from the Dockerfile in the repository
                          sh 'sudo docker build -t my-user .'
                          }
                     }
                 }
             }
        }        
        stage('Run Docker Image') {
            steps {
                script {
                    // Optionally run the Docker container to test it (useful for validation)
                    sh 'sudo docker run --name users.data -d my-user'
                }
            }
        }

        stage('Login to AWS ECR') {
            steps {
                script {
                    // Login to AWS ECR
                    sh '''
                    $(aws ecr get-login --no-include-email --region $AWS_REGION)
                    '''
                }
            }
        }
        stage('Tag Docker Image') {
            steps {
                script {
                    // Tag Docker image with the ECR repository URL
                    sh '''
                    sudo docker tag my-app:$BUILD_NUMBER $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
                    '''
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                script {
                    // Push the Docker image to AWS ECR
                    sh '''
                    sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
                    '''
                }
            }
        }

        stage('Deploy to Lambda') {
            steps {
                script {
                    // Update Lambda function with the new Docker image from ECR
                    sh '''
                    aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$latest
                    '''
                }
            }
        }
    }
    post {
        always {
            cleanWs()  // Clean up workspace after the pipeline
        }
    }
}
