# data-pipeline
 This project automates data integration by reading data from S3 and pushing it to RDS or AWS Glue using a Python program containerized with Docker. It leverages Terraform for infrastructure provisioning and Jenkins for a CI/CD    pipeline, ensuring seamless deployment and scalability.

# Step-by-Step Explanation
# Step 1: Project Goals
     The primary objectives of this project are:
   1.Automate data handling from AWS S3 to AWS RDS or AWS Glue.
   2.Use Docker to containerize the application for portability.
   3.Deploy the container to AWS ECR and use Lambda for execution.
   4.Set up a Jenkins CI/CD pipeline for automation.
   5.Use Terraform for infrastructure as code.

# Step 2: IAM Role & Policies 
     Create and IAM User and attach the all necessary policies to the user so it can work without any error.

# Step 3: Application Development
1. Python Script: 
This script will reads or create a .zip file and push it to S3 bucket and extract a .csv file and processes its content. Pushes the data to either RDS or AWS Glue.

 2.Create a Docker files :
     For creating a docker image of this application we need to create Dockerfile which will help us to make and image of this application.Create requirement files name it requirements.txt help to install the dependencies. Environment 
     variable file named as .env.

# Step 4: Infrastructure Setup using Terraform 

1.List of services which we will need to create for this application.  
  S3 bucket 
  RDS database 
  AWS Glue 
  ECR repository 
  Lambda function 
  IAM role and Policies for Lambda , RDS & AWS glue databases

# Step 5: CI/CD Pipeline using Jenkins 
  1.Jenkins Pipeline:
         Automated the Docker image building and running the container and deploy the Docker image to ECR repository to build a Lambda function.




