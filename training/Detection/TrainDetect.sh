#!/bin/bash 

#start virtual env
source detection/bin/activate

declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="Detection"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r TRAIN_DIR="${BUCKET}/${MODEL_NAME}/${JOB_ID}"
#Converted labeled records to TFrecords format
python PrepareData.py

#copy tfrecords and config file to the cloud
gsutil cp -r/Users/Ben/Dropbox/GoogleCloud/Detection/tfrecords/ gs://api-project-773889352370-ml/Detection/
gsutil cp faster_rcnn_inception_resnet_v2_atrous_coco.config gs://api-project-773889352370-ml/Detection/


#package to send to the cloud
cd models/research

python setup.py sdist
(cd slim && python setup.py sdist)

gcloud ml-engine jobs submit training ${JOB_ID} \
    --job-dir=gs://${TRAIN_DIR} \
    --packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz \
    --module-name object_detection.train \
    --region us-central1 \
    --config cloud.yaml \
    -- \
    --train_dir=gs://${TRAIN_DIR} \
    --pipeline_config_path= #Should this be local or cloud path?

tensorboard — logdir=gs://${TRAIN_DIR}
