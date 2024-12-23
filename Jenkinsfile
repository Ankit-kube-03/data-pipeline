pipeline {
    agent any
    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')  
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')  
        AWS_REGION = 'us-east-1'  // Set your AWS region
        ECR_REPOSITORY = 'data-pipeline-app'
        LAMBDA_FUNCTION_NAME = 'data-pipeline-function'  
        AWS_ACCOUNT_ID = '804425018582'  
    }
    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Ankit-kube-03/data-pipeline.git' 
                branch 'main'
            }
        }
        stage('Build Docker Image') {
             steps {
                 dir('data-pipeline') {
                     script {
                          node{
                          sh 'sudo docker build -t my-user .'
                          }
                     }
                 }
             }
        }        
        stage('Run Docker Image') {
            steps {
                script {
                    sh 'sudo docker run --env-file /var/lib/jenkins/workspace/data-pipeline@2/.env my-user'
                }
            }
        }
        
        stage('Tag Docker Image') {
            steps {
                script {
                    sh '''
                    sudo docker tag my-user:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
                    '''
                }
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                script {
                    sh '''
                    sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
                    '''
                }
            }
        }
    }
        
    post {
        always {
            cleanWs()  
        }
    }
}

