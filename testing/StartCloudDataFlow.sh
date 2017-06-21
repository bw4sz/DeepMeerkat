#! /bin/bash 

PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

python prediction/run.py \
    --runner DataflowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-prediction-cs \
    --setup_file prediction/setup.py \
    --model $BUCKET/model \
    --source cs \
    --input $BUCKET/input/images.txt \
    --output $BUCKET/output/predict