#! /bin/bash 
gcloud compute ssh cloudml 

sudo docker run -it --privileged -- gcr.io/api-project-773889352370/gcloudenv 

#clone repo
git clone https://github.com/bw4sz/DeepMeerkat.git
cd DeepMeerkat

PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

#copy most recent DeepMeerkat in version control from main directory
cp -r DeepMeerkat/ tests/prediction/modules/

#generate manifest of objects for dataflow to process
python tests/CreateManifest.py

#still not getting the API patch
pip install apache_beam[gcp]

#get a copy of the opencv wheel


python tests/prediction/run.py \
    --runner DataflowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-deepmeerkat \
    --setup_file tests/prediction/setup.py \
    --extra_package 