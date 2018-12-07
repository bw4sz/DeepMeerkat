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
declare -r DICT_FILE=gs://api-project-773889352370-ml/Hummingbirds/dict.txt 
declare -r VERSION_NAME=Boris

#make sure paths are updated
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Positives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Positives
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Negatives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Negatives

#get eval set size
eval=$(gsutil cat gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv | wc -l)

############
#Train Model
############

#Create Docs
python CreateDocs.py


#python trainer/preprocess.py \
  #--input_dict "$DICT_FILE" \
  #--input_path "gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv" \
  #--output_path "${GCS_PATH}/preproc/eval" \
  #--cloud

#python trainer/preprocess.py \
  #--input_dict "$DICT_FILE" \
  #--input_path "gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv" \
  #--output_path "${GCS_PATH}/preproc/train" \
  #--cloud
  
  gcloud ml-engine jobs submit training "$JOB_ID"\
  --stream-logs \
  --module-name trainer.task \
  --package-path trainer \
  --staging-bucket "$BUCKET" \
  --region us-central1 \
  --runtime-version=1.10 \
  -- \
  --output_path "${GCS_PATH}/training" \
  --eval_data_paths "gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20181206_120021/preproc/eval*" \
  --train_data_paths "gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20181206_120021/preproc/train*"\
  --eval_set_size  ${eval} \
  --max_steps 5000
    
    
#Monitor
tensorboard --logdir ${GCS_PATH} 