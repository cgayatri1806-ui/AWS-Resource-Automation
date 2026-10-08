from flask import Flask, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

app = Flask(__name__)
CORS(app)

# AWS Configuration
PROFILE_NAME = "aws-resource-automation"
REGION = "ap-south-1"
TARGET_INSTANCE_ID = "i-00918e05bda3a0d36"

session = boto3.Session(
    profile_name=PROFILE_NAME,
    region_name=REGION
)

ec2 = session.client("ec2")
s3 = session.client("s3")


@app.route("/")
def home():
    return jsonify({
        "message": "AWS Resource Automation API is running",
        "status": "success"
    })


@app.route("/api/status")
def status():
    try:
        response = ec2.describe_instances(
            InstanceIds=[TARGET_INSTANCE_ID]
        )

        instance = response["Reservations"][0]["Instances"][0]

        buckets = s3.list_buckets()["Buckets"]

        return jsonify({
            "success": True,
            "region": REGION,
            "account": "411217899041",
            "ec2": {
                "instance_id": TARGET_INSTANCE_ID,
                "state": instance["State"]["Name"],
                "type": instance["InstanceType"]
            },
            "s3": {
                "bucket_count": len(buckets),
                "buckets": [
                    bucket["Name"] for bucket in buckets
                ]
            }
        })

    except ClientError as error:
        return jsonify({
            "success": False,
            "error": error.response["Error"]["Message"]
        }), 500


@app.route("/api/ec2/start", methods=["POST"])
def start_ec2():
    try:
        ec2.start_instances(
            InstanceIds=[TARGET_INSTANCE_ID]
        )

        with open("logs/activity.log", "a") as log:
            log.write(
                f"{datetime.now()} | "
                f"EC2 START | "
                f"{TARGET_INSTANCE_ID} | "
                f"SUCCESS\n"
            )

        return jsonify({
            "success": True,
            "message": "EC2 start request submitted."
        })

    except ClientError as error:
        return jsonify({
            "success": False,
            "error": error.response["Error"]["Message"]
        }), 500


@app.route("/api/ec2/stop", methods=["POST"])
def stop_ec2():
    try:
        ec2.stop_instances(
            InstanceIds=[TARGET_INSTANCE_ID]
        )

        with open("logs/activity.log", "a") as log:
            log.write(
                f"{datetime.now()} | "
                f"EC2 STOP | "
                f"{TARGET_INSTANCE_ID} | "
                f"SUCCESS\n"
            )

        return jsonify({
            "success": True,
            "message": "EC2 stop request submitted."
        })

    except ClientError as error:
        return jsonify({
            "success": False,
            "error": error.response["Error"]["Message"]
        }), 500


@app.route("/api/logs")
def get_logs():
    try:
        log_file = "logs/activity.log"

        with open(log_file, "r") as log:
            lines = log.readlines()

        return jsonify({
            "success": True,
            "logs": [line.strip() for line in lines[-20:]]
        })

    except FileNotFoundError:
        return jsonify({
            "success": True,
            "logs": []
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )