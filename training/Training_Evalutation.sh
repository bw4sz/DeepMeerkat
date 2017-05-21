#!/bin/bash 

#Start docker instance
sudo docker run -it --privileged -- gcr.io/api-project-773889352370/cloudmlengine 

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
    --output_dir "${GCS_PATH}/" \
    --sample_image_uri  gs://api-project-773889352370-ml/Hummingbirds/Positives/10000.jpg  
    
#Run evaluation predictions 
#Mount directory

# #make empty directory for mount
mkdir /mnt/gcs-bucket

# #give it permissions
chmod a+w /mnt/gcs-bucket

#MOUNT 
gcsfuse --implicit-dirs api-project-773889352370-ml ~/mnt/gcs-bucket

gsutil cp gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv .
head trainingdata.csv | cut -d ',' -f1 > eval.csv

#extract eval frames to predict
cat /mnt/gcs-bucket/Hummingbirds/testingdata.csv  | cut -f 1 -d "," | head -n 20 > eval_files.txt
#fix local mount path
sed "s|gs://api-project-773889352370-ml/|/mnt/gcs-bucket/|g" eval_files.txt  > jpgs.txt

#Batch prediction
JSON_INSTANCES=Instances_$(date +%Y%m%d_%H%M%S).json
python images_to_json.py -o $JSON_INSTANCES $(cat jpgs.txt)
gsutil cp $JSON_INSTANCES gs://api-project-773889352370-ml/Hummingbirds/Prediction/

JOB_NAME=predict_Meerkat_$(date +%Y%m%d_%H%M%S)
gcloud ml-engine jobs submit prediction $JOB_NAME \
    --model=$MODEL_NAME \
    --data-format=TEXT \
    --input-paths=gs://api-project-773889352370-ml/Hummingbirds/Prediction/$JSON_INSTANCES \
    --output-path=gs://api-project-773889352370-ml/Hummingbirds/Prediction/ \
    --region=us-central1
    
#TODO RUN Out of sample predictions

#Python script to compute confusion matrix?


exit

