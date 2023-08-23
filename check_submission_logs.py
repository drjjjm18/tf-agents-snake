import argparse

import boto3
import botocore

BUCKET = "pavlovs-snake-submissions"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("team")
    parser.add_argument("submission_filename")

    args = parser.parse_args()
    team = args.team
    fname = args.submission_filename
    fname = f"{fname}.zip" if not fname.endswith(".zip") else fname

    s3 = boto3.client("s3")

    # Fetch the logs from the bucket
    try:
        obj = s3.get_object(
            Bucket=BUCKET,
            Key=f"{team}/{fname}.log"
        )
    except botocore.exceptions.ClientError as e:
        if "AccessDenied" in str(e):
                print("Failed to read logs, user is unauthorized get log file. Make sure that you:")
                print("\tHave provided the credentials correctly (follow https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)")
                print("\tHave specified the correct team name and submission name")
                print("\tHave not tampered with the check_submission_logs.py script. If so please checkout the version on the main branch")
                print("\tIf you have multiple AWS profiles, you have selected the correct one with 'export AWS_PROFILE=<profile name>'")
                print("It might also be that the submission has not been processed yet. If that is the case, please try again later.")
        else:
            raise e
    else:
        print(f"Logs from submission {fname}:\n")
        print(obj["Body"].read().decode())
