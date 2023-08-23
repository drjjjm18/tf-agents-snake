import os
import os.path as osp
import argparse
import tempfile
import zipfile
import datetime
import re

import boto3


SUBMISSION_FILES = [
    "user_agent.py",
    "user_eval_fn.py",
    "user_obs_fn.py",
    "user_rew_fn.py",
    "user_train.py"
]

SUBMISSION_MODEL_FOLDER = "model/"

SUBMISSION_BUCKET = "pavlovs-snake-submissions"

TEAM_NAME_SANITIZER = lambda x: re.sub("[^A-Za-z0-9-]+", "-" , x)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("team_name")
    args = parser.parse_args()


    compression = zipfile.ZIP_DEFLATED

    submission_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".zip"

    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = osp.join(tmp_dir, submission_file)
        # Zip relevant files
        with zipfile.ZipFile(archive_path, mode="w") as zf:
            for fname in SUBMISSION_FILES:
                if not osp.exists(fname):
                    raise RuntimeError(f"File {fname} is not present in the directory of the make_submission.py script")
                zf.write(fname, fname, compress_type=compression)

            if not osp.isdir(SUBMISSION_MODEL_FOLDER):
                raise RuntimeError(f"Folder {SUBMISSION_MODEL_FOLDER} is not present in the directory of the make_submission.py script")
            for dname, _, filenames in os.walk(SUBMISSION_MODEL_FOLDER):
                for filename in filenames:
                    zf.write(osp.join(dname, filename), compress_type=compression)

        # Upload the file to S3
        s3 = boto3.client("s3")
        team_folder = TEAM_NAME_SANITIZER(args.team_name)
        try:
            s3.upload_file(archive_path, SUBMISSION_BUCKET, osp.join(team_folder, submission_file))
        except boto3.exceptions.S3UploadFailedError as e:
            if "AccessDenied" in str(e):
                print("Failed to upload submission, user is unauthorized to upload. Make sure that you:")
                print("\tHave provided the credentials correctly (follow https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)")
                print("\tHave specified the correct team name")
                print("\tHave not tampered with the make_submission.py script. If so please checkout the version on the main branch")
                print("\tIf you have multiple AWS profiles, you have selected the correct one with 'export AWS_PROFILE=<profile name>'")
            else:
                raise e
        else:
            print(f"Successful submission with filename '{submission_file}'\nFingers crossed...")
