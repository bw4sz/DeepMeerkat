#!/bin/bash 

#Startup script
#git clone https://github.com/bw4sz/DeepMeerkat.git
#cd DeepMeerkat/training

#start virtual env
source env/bin/activate

#make sure all requirements are upgraded
pip install -r requirements.txt

declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="DeepMeerkat"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"

#Create Docs
python CreateDocs.py

#get eval set size
eval=$(gsutil cat gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv | wc -l)

############
#Train Model
############

python pipeline.py \
    --project ${PROJECT} \
    --cloud \
    --train_input_path gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv \
    --eval_input_path gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv \
    --input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    --deploy_model_name "DeepMeerkat" \
    --gcs_bucket ${BUCKET} \
    --output_dir "${GCS_PATH}/"  \
    --eval_set_size  ${eval} 

#already preprocessed
#python pipeline.py \
    #--project ${PROJECT} \
    #--cloud \
    #--preprocessed_train_set gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20170913_075525/preprocessed/train* \
    #--preprocessed_eval_set gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20170913_075525/preprocessed/eval* \
    #--input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    #--deploy_model_name "DeepMeerkat" \
    #--gcs_bucket ${BUCKET} \
    #--output_dir "${GCS_PATH}/" \
    #--eval_set_size  ${eval} 