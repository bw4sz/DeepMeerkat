#!/bin/bash 

#start virtual env
source env/bin/activate

#make sure all requirements are upgraded
pip install -r requirements.txt

declare  PROJECT=$(gcloud config list project --format "value(core.project)")
declare  BUCKET="gs://${PROJECT}-ml"
declare  MODEL_NAME="DeepMeerkat"
declare  JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare  GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"

#get eval set size
eval=$(gsutil cat gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv | wc -l)

############
#Train Model
############

#Create Docs
python CreateDocs.py

python pipeline.py \
    --project ${PROJECT} \
    --train_input_path gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv \
    --eval_input_path gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv \
    --input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    --gcs_bucket ${BUCKET} \
    --output_dir 
    
#Monitor
tensorboard --logdir ${GCS_PATH} 