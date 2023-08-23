import os
import os.path as osp
import re
import logging
import json
import time

import yaml
import boto3

logging.basicConfig(level=logging.INFO)

SUBMISSION_BUCKET = "pavlovs-snake-submissions"

TEAM_NAME_SANITIZER = lambda x: re.sub("[^A-Za-z0-9-]+", "-" , x)

def make_statement(team_name, arn):
    team_name = TEAM_NAME_SANITIZER(team_name)
    return {
        "Sid": team_name,
        "Effect": "Allow",
        "Principal": {
            "AWS": arn
        },
        "Action": "s3:PutObject",
        "Resource": f"arn:aws:s3:::{SUBMISSION_BUCKET}/{team_name}/*"
    }


if __name__ == "__main__":
    folder = osp.dirname(osp.abspath(__file__))

    # Create S3 client
    s3 = boto3.client("s3")
    # Load bucket policy
    policy = json.loads(s3.get_bucket_policy(Bucket=SUBMISSION_BUCKET)["Policy"])
    sids = [s["Sid"] for s in policy["Statement"]]

    # Create IAM client
    iam = boto3.client("iam")

    # Load teams from teams.yaml file and extract team names
    with open(osp.join(folder, "teams.yaml"), "r") as f:
        file_teams = yaml.safe_load(f)

    # Extract names and create a diff of those in need to be created or deleted
    team_names = list(map(TEAM_NAME_SANITIZER, [t["name"] for t in file_teams["teams"]]))
    aws_teams_names = list(map(lambda x: x["UserName"], iam.list_users(PathPrefix="/teams/")["Users"]))

    to_create = [n for n in team_names if n not in aws_teams_names]
    to_delete = [n for n in aws_teams_names if n not in team_names]


    # For each team to be created, create it, create keys and create bucket policy as needed
    for tname in to_create:
        logging.info(f"Creating user '{tname}'")
        user = iam.create_user(UserName=tname, Path="/teams/")["User"]

        user_created = False
        key_created = False

        try:
            # Create access key
            key = iam.create_access_key(UserName=tname)["AccessKey"]
            user_created = True

            # Save access key into file
            with open(osp.join(folder, f"keys/{tname}-key.txt"), "w") as f:
                f.write(f"aws_access_key_id = {key['AccessKeyId']}\n")
                f.write(f"aws_secret_access_key = {key['SecretAccessKey']}\n")
            key_created = True

            # Add statement to bucket policy for this user
            policy["Statement"].append(make_statement(tname, user["Arn"]))

        except Exception as e:
            logging.error(f"Error when creating team {tname}: {str(e)}")
            logging.info("Cleaning up...")
            if key_created:
                iam.delete_access_key(UserName=tname, AccessKeyId=key["AccessKeyId"])
                os.remove(osp.join(folder, f"keys/{tname}-key.txt"))
            if user_created:
                iam.delete_user(UserName=tname)


    # Remove teams not present anymore
    for tname in to_delete:
        logging.info(f"Deleting user {tname}")
        # Remove from bucket policies if there
        if tname in sids:
            policy["Statement"] = [s for s in policy["Statement"] if s["Sid"] != tname]
        
        # Remove key if exists
        for key in iam.list_access_keys(UserName=tname)["AccessKeyMetadata"]:
            iam.delete_access_key(UserName=tname, AccessKeyId=key["AccessKeyId"])

        if os.path.exists(osp.join(folder, f"keys/{tname}-key.txt")):
            os.remove(osp.join(folder, f"keys/{tname}-key.txt"))

        # Remove user
        iam.delete_user(UserName=tname)

    # Reapply policy on bucket
    # print(json.dumps(policy))
    if len(to_create) > 0:
        time.sleep(10)

    print(json.dumps(policy))
    s3.put_bucket_policy(Bucket=SUBMISSION_BUCKET, Policy=json.dumps(policy))

