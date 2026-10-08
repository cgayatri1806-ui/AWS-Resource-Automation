# AWS Resource Automation Dashboard using Python & Boto3

## 1. Project Objective

The objective of this project is to build a web dashboard that helps monitor AWS resources and perform basic EC2 instance operations using Python and Boto3.

## 2. Technologies Used

* Python
* Boto3
* Flask
* HTML
* CSS
* JavaScript
* Amazon EC2
* Amazon S3
* AWS IAM

## 3. Architecture

User → Web Dashboard → Flask API → Boto3 → AWS Services

The dashboard sends requests to the Flask API. The API uses Boto3 to communicate with AWS and returns resource information to the dashboard.

## 4. Project Features

* Display AWS account and region information.
* List S3 buckets.
* Display EC2 instance details and status.
* Start and stop an EC2 instance.
* Display activity logs.

## 5. How to Run

1. Open the project folder.
2. Activate the Python virtual environment.
3. Install the required Python packages.
4. Start the API using `python run_server.py`.
5. Start the dashboard server using `python -m http.server 8080 --directory dashboard`.
6. Open `http://127.0.0.1:8080/` in a browser.

## 6. AWS Region

`ap-south-1` (Mumbai)

## 7. Key Learnings

* Connected Python applications to AWS using Boto3.
* Retrieved AWS resource information.
* Practised EC2 instance management.
* Built a dashboard using Flask and web technologies.
* Displayed activity logs and AWS resource status.

## 8. Screenshots

Add actual project screenshots in a folder named `screenshots` and link them here.

## 9. Security

AWS credentials are not included in this project. Use secure AWS credential configuration and grant only the permissions required by the application.
