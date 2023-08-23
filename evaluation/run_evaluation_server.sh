#!/usr/bin/env bash

## Script to handle the async submission process on the EC2 instance

# --- VARS --- #
GH_REPO="git@github.com:danalyticsuk/pavlovs-snake.git"
GH_REPO_NAME="pavlovs-snake"
QUEUE_URL="https://sqs.eu-west-2.amazonaws.com/734197760602/submissions.fifo"
WORKDIR="$PWD"
VENV_PATH="$WORKDIR/envs"
VENV_NAME="myenv"

# End script if no message is received for this many seconds
# Set it to -1 to never terminate
TERMINATE_AFTER=-1

# --- SCRIPT --- #
mkdir -p logs
{
    # Change dir to work dir
    cd "$WORKDIR"

    # Clone main repo and checkout latest main (can fail the cloning if exists already)
    echo "Setting up the repository"
    if [ ! -d "$WORKDIR/$GH_REPO_NAME" ]; then
        git clone $GH_REPO
    fi
    cd "$GH_REPO_NAME"
    git fetch && git reset --hard origin/main && git clean -fd

    # Create environment if it does not exist
    echo "Setting up the python environment"
    mkdir -p "$VENV_PATH"
    if [ -d "$VENV_PATH/$VENV_NAME" ]; then
        echo "Environment exists already, activating it"
    else
        python3 -m venv "$VENV_PATH/$VENV_NAME"
    fi

    # Setup environment
    source "$VENV_PATH/$VENV_NAME/bin/activate"
    python3 -m pip install -r requirements.txt


    # Listen for submissions and process them
    cd "$WORKDIR"
    CONTINUE=true
    LAST_RECEIVED=$SECONDS
    echo "Starting to listen for submissions"

    while $CONTINUE; do
        MSG=$(aws sqs receive-message \
                --queue-url $QUEUE_URL \
                --wait-time-seconds 10 | awk -F '\t' '{print $2}')
        if [ ! -z "$MSG" ]; then
            # A message was received, process submission
            LAST_RECEIVED=$SECONDS
            echo "Processing submission: $MSG"

            OUT="$(./evaluate_submission.sh "$MSG" 2>&1)"
            EXIT_CODE=$?
            if [ "$EXIT_CODE" -eq  "0" ]; then
                TEAM=$(echo $MSG | sed 's|s3://.*/\([^ /]*\)/.*|\1|')
                echo "Successfully processed submission:"
                printf "\n--------------------------------------\n\n"
                echo "team_name: $TEAM"
                echo "$OUT"
                printf "\n--------------------------------------\n\n"
                python update_score.py ../Leaderboard/src/data/database.json $TEAM "$OUT"
            else
                echo "Failed to evaluate submission, error is as follows:"
                printf "\n--------------------------------------\n\n"
                echo "$OUT"
                printf "\n--------------------------------------\n\n"
                sleep 5
            fi

            # Output logs to S3
            echo "$OUT" - | aws s3 cp - "$MSG.log"

            echo "Processing done, removing from queue"

            RECEIPT=$(aws sqs receive-message --queue-url $QUEUE_URL | awk -F '\t' '{print $5}')
            aws sqs delete-message \
                --queue-url $QUEUE_URL \
                --receipt-handle "$RECEIPT"

            if [ $? -ne "0" ]; then
                echo "An error happened while trying to delete a message, stopping"
                CONTINUE=false
            fi
        elif [ "$TERMINATE_AFTER" -gt "-1" ] && [[ "$(($SECONDS - $LAST_RECEIVED))" -ge "$TERMINATE_AFTER" ]]; then
            echo "No message received for $TERMINATE_AFTER seconds, exiting..."
            CONTINUE=false
        fi
    done

    echo "No more messages in queue, shutting down..."
} 2>&1 | ts '[%Y-%d-%m %H:%M:%S]' | tee "./logs/$(date '+%Y-%d-%m %H-%M-%S').log"
