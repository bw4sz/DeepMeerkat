#!/bin/bash 

#start virtual env
#source env/bin/activate

#make sure all requirements are upgraded
#pip install -r requirements.txt

declare  PROJECT=$(gcloud config list project --format "value(core.project)")
declare  BUCKET="gs://${PROJECT}-ml"
declare  MODEL_NAME="DeepMeerkat"
declare  JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare  GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"
declare  DATA_PATH="${BUCKET}/Viivi_Fish"
declare -r DICT_FILE="${DATA_PATH}/dict.txt"
declare -r VERSION_NAME=Viivi_Fish

#make sure paths are updated to your google Cloud
gsutil rsync -d /Users/ben/Dropbox/Training_clips/Training/Positives/ "${DATA_PATH}"/Training/Positives
gsutil rsync -d /Users/ben/Dropbox/Training_clips/Training/Negatives/ "${DATA_PATH}"/Training/Negatives

gsutil rsync -d /Users/ben/Dropbox/Training_clips/Testing/Positives/ "${DATA_PATH}"/Testing/Positives
gsutil rsync -d /Users/ben/Dropbox/Training_clips/Testing/Negatives/ "${DATA_PATH}"/Testing/Negatives


#get eval set size
eval=$(gsutil cat "${DATA_PATH}"/testingdata.csv | wc -l)

############
#Train Model
############

#Create Docs
python CreateDocs.py --DATA_PATH "${DATA_PATH}"

python trainer/preprocess.py \
  --input_dict "$DICT_FILE" \
  --input_path ""${DATA_PATH}"/testingdata.csv" \
  --output_path "${GCS_PATH}/preproc/eval" \
  --cloud

python trainer/preprocess.py \
  --input_dict "$DICT_FILE" \
  --input_path ""${DATA_PATH}"/trainingdata.csv" \
  --output_path "${GCS_PATH}/preproc/train" \
  --cloud
  
  gcloud ml-engine jobs submit training "$JOB_ID"\
  --stream-logs \
  --module-name trainer.task \
  --package-path trainer \
  --staging-bucket "$BUCKET" \
  --region us-central1 \
  --runtime-version=1.10 \
  -- \
  --output_path "${GCS_PATH}/training" \
  --eval_data_paths "${GCS_PATH}/preproc/eval*" \
  --train_data_paths "${GCS_PATH}/preproc/train*"\
  --eval_set_size  ${eval} \
  --max_steps 2000
    
#Monitor
tensorboard --logdir ${GCS_PATH} 