#!/bin/bash 

#start virtual env
source detection/bin/activate

#Converted labeled records to TFrecords format
python PrepareData.py

#copy tfrecords to the cloud
gsutil cp /Users/Ben/Dropbox/GoogleCloud/Detection/tfrecords/ gs://api-project-773889352370-ml/Detection/

declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="DeepMeerkatDetection"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r TRAIN_DIR="${BUCKET}/${MODEL_NAME}/${JOB_ID}"

# From tensorflow/models/research/
gcloud ml-engine jobs submit training object_detection_`date +%s` \
    --job-dir=gs://${TRAIN_DIR} \
    --packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz \
    --module-name object_detection.train \
    --region us-central1 \
    --config cloud.yaml \
    -- \
    --train_dir=gs://${TRAIN_DIR} \
    --pipeline_config_path=faster_rcnn_inception_resnet_v2_atrous_coco.config #Should this be local or cloud path?

tensorboard — logdir=gs://${TRAIN_DIR}
