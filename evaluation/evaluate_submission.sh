#!/usr/bin/env bash

set -e

# --- VARS --- #
GH_REPO_NAME="pavlovs-snake"
WORKDIR="$PWD"
ARCHIVE_URI=$1
USER_FILES=("user_agent.py" "user_eval_fn.py" "user_obs_fn.py" "user_rew_fn.py" "user_train.py")
MODEL_FOLDER="model/"
TIMEOUT=300s

if [ -z "$ARCHIVE_URI" ]; then
    echo "Argument required s3-archive"
    exit 1
fi


# --- SCRIPT ---#

cd "$WORKDIR/$GH_REPO_NAME"

# Remove files
rm -rf ${USER_FILES[@]} $MODEL_FOLDER submissions

# Create the submission folder 
mkdir submissions
aws s3 cp $ARCHIVE_URI submissions/submission.zip > /dev/null

# Unzip the submission files to the CWD
unzip submissions/submission.zip > /dev/null

set +e

# Run evaluation
timeout --preserve-status $TIMEOUT python3 evaluate_agent.py model
exit_code=$?

if [ "$exit_code" -eq "143" ]; then
    echo "Submission was terminated as it took more than $TIMEOUT"
    exit 1
elif [ "$exit_code" -ne "0" ]; then
    exit 1
fi
