#!/bin/bash 

declare PROJECT=$(gcloud config list project --format "value(core.project)")
declare BUCKET="gs://${PROJECT}-ml"
declare MODEL_NAME="DeepMeerkatDetection"
declare FOLDER="${BUCKET}/${MODEL_NAME}"
declare JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare TRAIN_DIR="${FOLDER}/${JOB_ID}/train"
declare EVAL_DIR="${BUCKET}/${MODEL_NAME}/${JOB_ID}/eval"
#Switch from local to cloud config files
#declare  PIPELINE_CONFIG_PATH="/Users/ben/Documents/DeepMeerkat/training/Detection/faster_rcnn_inception_resnet_v2_atrous_coco.config"
declare  PIPELINE_CONFIG_PATH="${FOLDER}/pipeline.config"
declare  PIPELINE_YAML="/Users/Ben/Documents/DeepMeerkat/training/Detection/cloud.yml"

#Converted labeled records to TFrecords format
python PrepareData.py

#copy tfrecords and config file to the cloud
gsutil cp -r /Users/Ben/Dropbox/GoogleCloud/Detection/tfrecords ${FOLDER}
gsutil cp pipeline.config ${FOLDER}
gsutil cp label.pbtxt ${FOLDER}

#upload checkpoint if it doesn't exist
gsutil cp  -r checkpoint/ ${FOLDER}
    
#package to send to the cloud
python setup.py sdist
(cd slim && python setup.py sdist)

#Training

##Local
##source env

#set build
protoc object_detection/protos/*.proto --python_out=.

#add path
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
python object_detection/builders/model_builder_test.py

#train
python object_detection/train.py \
    --logtostderr \
    --pipeline_config_path=/Users/ben/Documents/DeepMeerkat/training/Detection/faster_rcnn_inception_resnet_v2_atrous_coco.config \
    --train_dir=/Users/Ben/Dropbox/GoogleCloud/Detection/train/
    
#eval
# From the tensorflow/models/research/ directory
python object_detection/eval.py \
    --logtostderr \
    --pipeline_config_path=/Users/ben/Documents/DeepMeerkat/training/Detection/faster_rcnn_inception_resnet_v2_atrous_coco.config \
    --checkpoint_dir=/Users/Ben/Dropbox/GoogleCloud/Detection/train/ \
    --eval_dir=/Users/Ben/Dropbox/GoogleCloud/Detection/eval/

#local tensorflow
tensorboard --logdir /Users/Ben/Dropbox/GoogleCloud/Detection/
    
#Cloud
gcloud ml-engine jobs submit training "${JOB_ID}_train" \
    --job-dir=${TRAIN_DIR} \
    --packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz \
    --module-name object_detection.train \
    --region us-central1 \
    --config object_detection/samples/cloud/cloud.yml \
    -- \
    --train_dir=${TRAIN_DIR} \
    --pipeline_config_path=gs://api-project-773889352370-ml/DeepMeerkatDetection/pipeline.config

#evalution job
gcloud ml-engine jobs submit training object_detection_eval_`date +%s` \
    --job-dir=${TRAIN_DIR} \
    --packages dist/object_detection-0.1.tar.gz,slim/dist/slim-0.1.tar.gz \
    --module-name object_detection.eval \
    --region us-central1 \
    --scale-tier BASIC_GPU \
    -- \
    --checkpoint_dir=${TRAIN_DIR} \
    --eval_dir=${EVAL_DIR} \
    --pipeline_config_path=gs://api-project-773889352370-ml/DeepMeerkatDetection/pipeline.config
    
tensorboard --logdir=${TRAIN_DIR}

#export graph, need to update checkpoint number
python object_detection/export_inference_graph.py \
    --input_type image_tensor \
    --pipeline_config_path ${PIPELINE_CONFIG_PATH} \
    --trained_checkpoint_prefix /Users/Ben/Dropbox/GoogleCloud/Detection/train/model.ckpt-186\
    --output_directory /Users/Ben/Dropbox/GoogleCloud/Detection/SavedModel/