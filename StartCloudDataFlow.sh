#! /bin/bash

PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

#generate manifest of objects for dataflow to process
python CreateManifest.py

#testing without tensorflow
python run_clouddataflow.py \
    --runner DataFlowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-deepmeerkat \
    --setup_file ./setup.py \
    --draw_box
