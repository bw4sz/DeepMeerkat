#!/bin/bash 

#ssh if needed
#gcloud compute ssh cloudml 

#Start docker instance
sudo docker run -it --privileged -- gcr.io/api-project-773889352370/cloudmlengine 

#Startup script
git clone https://github.com/bw4sz/DeepMeerkat.git
cd DeepMeerkat/training

#make sure all requirements are upgraded
#pip install -r requirements.txt

declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="DeepMeerkat"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"

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
    --output_dir "${GCS_PATH}/" \
    --sample_image_uri  gs://api-project-773889352370-ml/Hummingbirds/Positives/10000.jpg  

exit

