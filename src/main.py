
import boto3
import csv
import os
from datetime import datetime
from botocore.exceptions import ClientError

# ============================================================
# AWS SESSION
# ============================================================

session = boto3.Session(
    profile_name="aws-resource-automation",
    region_name="ap-south-1"
)

# ============================================================
# AWS ACCOUNT INFORMATION
# ============================================================

sts = session.client("sts")
account = sts.get_caller_identity()

print("=" * 60)
print("       AWS RESOURCE AUTOMATION DASHBOARD")
print("=" * 60)

print("Account :", account["Account"])
print("User    :", account["Arn"])
print("Region  : ap-south-1")

# ============================================================
# INITIALIZE REPORT
# ============================================================

report_rows = []
checked_at = datetime.now().isoformat(timespec="seconds")

# ============================================================
# S3 RESOURCE HEALTH CHECK
# ============================================================

s3 = session.client("s3")

print("\n" + "=" * 60)
print("S3 RESOURCE HEALTH CHECK")
print("=" * 60)

bucket_count = 0

try:
    response = s3.list_buckets()
    buckets = response.get("Buckets", [])
    bucket_count = len(buckets)

    print("Total S3 Buckets:", bucket_count)

    for bucket in buckets:
        bucket_name = bucket["Name"]
        file_count = 0

        print("\nBucket Name:", bucket_name)
        print("Created    :", bucket["CreationDate"])

        try:
            # Count all objects, including those beyond the first page.
            paginator = s3.get_paginator("list_objects_v2")

            for page in paginator.paginate(Bucket=bucket_name):
                objects = page.get("Contents", [])

                for obj in objects:
                    file_count += 1
                    print("  -", obj["Key"])

            print("File Count :", file_count)

            report_rows.append({
                "Resource Type": "S3 Bucket",
                "Resource Name": bucket_name,
                "Status": "Available",
                "Details": f"Object count: {file_count}",
                "Checked At": checked_at
            })

        except ClientError as error:
            error_code = error.response["Error"]["Code"]

            print("Unable to list bucket objects:", error_code)

            report_rows.append({
                "Resource Type": "S3 Bucket",
                "Resource Name": bucket_name,
                "Status": "Check Failed",
                "Details": error_code,
                "Checked At": checked_at
            })

        print("-" * 60)

except ClientError as error:
    print("S3 check failed:", error.response["Error"]["Code"])

# ============================================================
# EC2 RESOURCE HEALTH CHECK
# ============================================================

ec2 = session.client("ec2")

print("\n" + "=" * 60)
print("EC2 RESOURCE HEALTH CHECK")
print("=" * 60)

instance_count = 0

try:
    paginator = ec2.get_paginator("describe_instances")

    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                instance_count += 1

                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]
                instance_type = instance["InstanceType"]

                print("Instance ID :", instance_id)
                print("State       :", state)
                print("Type        :", instance_type)

                if state == "running":
                    health_status = "HEALTHY - Running"
                elif state == "stopped":
                    health_status = "STOPPED"
                elif state == "terminated":
                    health_status = "TERMINATED"
                else:
                    health_status = state.upper()

                print("Health      :", health_status)
                print("-" * 60)

                report_rows.append({
                    "Resource Type": "EC2 Instance",
                    "Resource Name": instance_id,
                    "Status": state,
                    "Details": (
                        f"Instance type: {instance_type}; "
                        f"Health: {health_status}"
                    ),
                    "Checked At": checked_at
                })

    print("Total EC2 Instances:", instance_count)

    if instance_count == 0:
        print("No EC2 instances found.")

except ClientError as error:
    print("EC2 check failed:", error.response["Error"]["Code"])

# ============================================================
# EC2 START / STOP AUTOMATION
# ============================================================

print("\n" + "=" * 60)
print("EC2 START / STOP AUTOMATION")
print("=" * 60)

# Existing instance; this code does not create an instance.
TARGET_INSTANCE_ID = "i-00918e05bda3a0d36"

try:
    target_response = ec2.describe_instances(
        InstanceIds=[TARGET_INSTANCE_ID]
    )

    target_instances = [
        instance
        for reservation in target_response["Reservations"]
        for instance in reservation["Instances"]
    ]

    if not target_instances:
        print("Target EC2 instance was not found.")

    else:
        target_instance = target_instances[0]
        current_state = target_instance["State"]["Name"]

        print("Target Instance :", TARGET_INSTANCE_ID)
        print("Current State   :", current_state)

        if current_state == "stopped":
            print("1. Start EC2")
        elif current_state == "running":
            print("1. Stop EC2")
        else:
            print("No Start/Stop action available.")
            current_state = "not-actionable"

        if current_state in ["stopped", "running"]:
            choice = input(
                "\nEnter 1 to perform the action, "
                "or press Enter to skip: "
            ).strip()

            if choice == "1":
                confirmation = input(
                    "Type YES to confirm the action: "
                ).strip()

                if confirmation == "YES":
                    try:
                        if current_state == "stopped":
                            ec2.start_instances(
                                InstanceIds=[TARGET_INSTANCE_ID]
                            )
                            action = "START"
                        else:
                            ec2.stop_instances(
                                InstanceIds=[TARGET_INSTANCE_ID]
                            )
                            action = "STOP"

                        print(f"{action} request submitted.")

                        os.makedirs("logs", exist_ok=True)

                        with open(
                            "logs/activity.log",
                            "a",
                            encoding="utf-8"
                        ) as log:
                            log.write(
                                f"{datetime.now().isoformat()} | "
                                f"EC2 {action} | "
                                f"{TARGET_INSTANCE_ID} | "
                                "Request submitted\n"
                            )

                    except ClientError as error:
                        print(
                            "EC2 action failed:",
                            error.response["Error"]["Code"]
                        )
                else:
                    print("Action cancelled.")
            else:
                print("No EC2 action selected.")

except ClientError as error:
    print("EC2 automation failed:", error.response["Error"]["Code"])

# ============================================================
# IAM USER HEALTH CHECK
# ============================================================

print("\n" + "=" * 60)
print("IAM USER HEALTH CHECK")
print("=" * 60)

iam_user_count = 0
iam = session.client("iam")

try:
    paginator = iam.get_paginator("list_users")

    for page in paginator.paginate():
        for user in page["Users"]:
            iam_user_count += 1

            username = user["UserName"]

            print("IAM User:", username)
            print("Created :", user["CreateDate"])
            print("-" * 60)

            report_rows.append({
                "Resource Type": "IAM User",
                "Resource Name": username,
                "Status": "Listed",
                "Details": "IAM user detected",
                "Checked At": checked_at
            })

    print("Total IAM Users:", iam_user_count)

except ClientError as error:
    print("IAM check failed:", error.response["Error"]["Code"])

# ============================================================
# CSV REPORT EXPORT
# ============================================================

os.makedirs("reports", exist_ok=True)

report_file = os.path.join(
    "reports",
    f"aws_resource_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)

fieldnames = [
    "Resource Type",
    "Resource Name",
    "Status",
    "Details",
    "Checked At"
]

with open(
    report_file,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(report_rows)

print("\n" + "=" * 60)
print("CSV REPORT EXPORT")
print("=" * 60)
print("Report saved to:", report_file)
print("Rows exported :", len(report_rows))

# ============================================================
# DASHBOARD SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DASHBOARD SUMMARY")
print("=" * 60)

print("AWS Account   :", account["Account"])
print("S3 Buckets    :", bucket_count)
print("EC2 Instances :", instance_count)
print("IAM Users     :", iam_user_count)
print("Report Rows   :", len(report_rows))
print("Region        : ap-south-1")
print("=" * 60)
print("AWS RESOURCE AUTOMATION CHECK COMPLETED")
print("=" * 60)