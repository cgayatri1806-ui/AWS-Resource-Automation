import boto3
from datetime import datetime

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
print("           AWS RESOURCE AUTOMATION DASHBOARD")
print("=" * 60)

print("Account :", account["Account"])
print("User    :", account["Arn"])
print("Region  : ap-south-1")


# ============================================================
# S3 RESOURCE HEALTH CHECK
# ============================================================

s3 = session.client("s3")

response = s3.list_buckets()

print("\n" + "=" * 60)
print("S3 RESOURCE HEALTH CHECK")
print("=" * 60)

bucket_count = len(response["Buckets"])

print("Total S3 Buckets:", bucket_count)
print()

for bucket in response["Buckets"]:

    bucket_name = bucket["Name"]

    print("Bucket Name:", bucket_name)
    print("Created    :", bucket["CreationDate"])

    try:
        objects = s3.list_objects_v2(
            Bucket=bucket_name
        )

        if "Contents" in objects:

            file_count = len(objects["Contents"])

            print("File Count :", file_count)
            print("Files      :")

            for obj in objects["Contents"]:
                print("  -", obj["Key"])

        else:

            print("File Count : 0")
            print("Files      : No files")

    except Exception as error:

        print("Unable to read bucket objects.")
        print("Error:", error)

    print("-" * 60)


# ============================================================
# EC2 RESOURCE HEALTH CHECK
# ============================================================

ec2 = session.client("ec2")

instances = ec2.describe_instances()

print("\n" + "=" * 60)
print("EC2 RESOURCE HEALTH CHECK")
print("=" * 60)

instance_found = False
instance_count = 0

for reservation in instances["Reservations"]:

    for instance in reservation["Instances"]:

        instance_found = True
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
            health_status = "UNKNOWN"

        print("Health      :", health_status)

        print("-" * 60)


if not instance_found:

    print("No EC2 instances found.")

else:

    print("Total EC2 Instances:", instance_count)


# ============================================================
# EC2 START / STOP AUTOMATION
# ============================================================

print("\n" + "=" * 60)
print("EC2 START / STOP AUTOMATION")
print("=" * 60)

TARGET_INSTANCE_ID = "i-00918e05bda3a0d36"

try:

    target = ec2.describe_instances(
        InstanceIds=[TARGET_INSTANCE_ID]
    )

    target_instance = target["Reservations"][0]["Instances"][0]

    current_state = target_instance["State"]["Name"]

    print("Target Instance :", TARGET_INSTANCE_ID)
    print("Current State   :", current_state)

    print("\nAvailable Actions:")

    if current_state == "stopped":

        print("1. Start EC2")

    elif current_state == "running":

        print("1. Stop EC2")

    else:

        print("No Start/Stop action available for current state.")


    # ========================================================
    # USER ACTION
    # ========================================================

    if current_state in ["stopped", "running"]:

        choice = input(
            "\nEnter choice (1 or press Enter to skip): "
        ).strip()

        if choice == "1":

            confirmation = input(
                "Type YES to confirm the EC2 action: "
            ).strip()

            if confirmation == "YES":

                # ====================================================
                # START EC2
                # ====================================================

                if current_state == "stopped":

                    print("\nStarting EC2 instance...")

                    ec2.start_instances(
                        InstanceIds=[TARGET_INSTANCE_ID]
                    )

                    print(
                        "SUCCESS: EC2 start request submitted."
                    )

                    # Activity Log
                    with open(
                        "logs/activity.log",
                        "a"
                    ) as log:

                        log.write(
                            f"{datetime.now()} | "
                            f"EC2 START | "
                            f"{TARGET_INSTANCE_ID} | "
                            f"SUCCESS\n"
                        )


                # ====================================================
                # STOP EC2
                # ====================================================

                elif current_state == "running":

                    print("\nStopping EC2 instance...")

                    ec2.stop_instances(
                        InstanceIds=[TARGET_INSTANCE_ID]
                    )

                    print(
                        "SUCCESS: EC2 stop request submitted."
                    )

                    # Activity Log
                    with open(
                        "logs/activity.log",
                        "a"
                    ) as log:

                        log.write(
                            f"{datetime.now()} | "
                            f"EC2 STOP | "
                            f"{TARGET_INSTANCE_ID} | "
                            f"SUCCESS\n"
                        )


            else:

                print("Action cancelled.")


        else:

            print("No EC2 action selected.")


except Exception as error:

    print("EC2 automation error:")
    print(error)


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("DASHBOARD SUMMARY")
print("=" * 60)

print("AWS Account   :", account["Account"])
print("S3 Buckets    :", bucket_count)
print("EC2 Instances :", instance_count)

if instance_count == 0:

    print("EC2 Status    : No instances found")

else:

    print("EC2 Status    : Health check completed")


print("=" * 60)
print("AWS RESOURCE AUTOMATION CHECK COMPLETED")
print("=" * 60)

