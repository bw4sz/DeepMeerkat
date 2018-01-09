#!/bin/bash 

#start virtual env
source env/bin/activate

#make sure all requirements are upgraded
#pip install -r requirements.txt

declare  PROJECT=$(gcloud config list project --format "value(core.project)")
declare  BUCKET="gs://${PROJECT}-ml"
declare  MODEL_NAME="DeepMeerkat"
declare  JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare  GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"

#make sure paths are updated
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Positives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Positives
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Negatives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Negatives


#get eval set size
eval=$(gsutil cat gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv | wc -l)

############
#Train Model
############

#Create Docs
#python CreateDocs.py

#python pipeline.py \
    #--project ${PROJECT} \
    #--cloud \
    #--train_input_path gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv \
    #--eval_input_path gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv \
    #--input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    #--deploy_model_name "DeepMeerkat" \
    #--gcs_bucket ${BUCKET} \
    #--output_dir "${GCS_PATH}/"  \
    #--eval_set_size  ${eval} 



#already preprocessed
python pipeline.py \
    --project ${PROJECT} \
    --cloud \
    --preprocessed_train_set gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20180108_205121/preprocessed/train* \
    --preprocessed_eval_set gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20180108_205121/preprocessed/eval* \
    --input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    --deploy_model_name "DeepMeerkat" \
    --gcs_bucket ${BUCKET} \
    --output_dir "${GCS_PATH}/" \
    --eval_set_size  ${eval} 
    
    
#Monitor
tensorboard --logdir ${GCS_PATH} 