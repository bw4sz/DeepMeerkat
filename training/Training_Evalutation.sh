#!/bin/bash 

#Start docker instance
docker run -it -- gcr.io/api-project-773889352370/cloudmlengine 

#Startup script
git clone https://github.com/bw4sz/DeepMeerkat.git
cd DeepMeerkat/training


declare -r USER="Ben"
declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r JOB_ID="DeepMeerkat_${USER}_$(date +%Y%m%d_%H%M%S)"
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r GCS_PATH="${BUCKET}/${USER}/${JOB_ID}"
declare -r MODEL_NAME="DeepMeerkat"

#TODO if model name exists:

#from scratch
python pipeline.py \
    --project ${PROJECT} \
    --cloud \
    --train_input_path gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv \
    --eval_input_path gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv \
    --input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    --deploy_model_name "DeepMeerkat" \
    --gcs_bucket ${BUCKET} \
    --output_dir "${GCS_PATH}/training" \
    --sample_image_uri  gs://api-project-773889352370-ml/Hummingbirds/Positives/10000.jpg  
    
#Run evaluation predictions 
gsutil cp gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv .
head trainingdata.csv | cut -d ',' -f1 > eval.csv

#get json request file
python images_to_json.py -o request.json $(cat eval.csv)
gsutil cp eval.csv gs://api-project-773889352370-ml/Hummingbirds/request.json

gcloud ml-engine jobs submit prediction "DeepMeerkat_$(date +%Y%m%d_%H%M%S)" 
    --model "DeepMeerkat"
    --input-paths gs://api-project-773889352370-ml/Hummingbirds/request.json
    --output-path gs://api-project-773889352370-ml/Hummingbirds/Prediction/ 
    --region us-central1 
    --data-format TEXT
    
#TODO RUN Out of sample predictions

#Python script to compute confusion matrix

#COPY analysis results to file

exit

