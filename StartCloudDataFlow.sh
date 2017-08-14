#! /bin/bash

#sudo docker run -it --privileged -- gcr.io/api-project-773889352370/gcloudenv

#clone repo
#git clone https://github.com/bw4sz/DeepMeerkat.git
#cd DeepMeerkat

PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

#generate manifest of objects for dataflow to process
python CreateManifest.py

#still not getting the API patch
#pip install apache_beam[gcp]
#pip install google.cloud

#get newest model
#curl -L https://www.dropbox.com/sh/s34q9m7lkyfz12t/AADj8LdHd16dEssbKZCF-Ihma?dl=1 > model.zip
#unzip -o model.zip -d /DeepMeerkat/model

#testing without tensorflow
python run_clouddataflow.py \
    --runner DataflowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-deepmeerkat \
    --setup_file setup.py \
    --maxNumWorkers 2 \
    --path_to_model "model/" \
    --tensorflow \
    --training
