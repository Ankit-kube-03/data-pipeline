pipeline {
    agent any  // This will run the pipeline on any available agent

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Terraform: Init') {
            steps {
                sh 'terraform init'
            }
        }

        stage('Terraform: Plan') {
            steps {
                sh 'terraform plan -out=tfplan'
            }
        }

        stage('Terraform: Apply') {
            steps {
                sh 'terraform apply tfplan'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t python-app .'
            }
        }

        stage('Push Docker Image to ECR') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-access-key-id', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    sh '''aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin your-ecr-repository'''
                    sh '''docker tag python-app:latest your-ecr-repository:latest'''
                    sh '''docker push your-ecr-repository:latest'''
                }
            }
        }

        stage('Deploy Lambda Function') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-access-key-id', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) {
                    sh '''aws lambda create-function \
                        --function-name python-lambda \
                        --package-type Image \
                        --code ImageUri=your-ecr-repository:latest \
                        --role arn:aws:iam::123456789012:role/lambda-role \
                        --timeout 900 --memory-size 512'''
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh 'terraform destroy -auto-approve'
            }
        }
    }

    post {
        always {
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
