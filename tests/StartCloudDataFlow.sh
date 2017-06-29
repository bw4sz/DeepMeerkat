#! /bin/bash 

sudo docker run -it --privileged -- gcr.io/api-project-773889352370/gcloudenv 

PROJECT=$(gcloud.cmd config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

#copy most recent DeepMeerkat in version control from main directory
cp -r ../DeepMeerkat/ prediction/modules/

#generate manifest of objects for dataflow to process
python CreateManifest.py

python prediction/run.py \
    --runner DataflowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-deepmeerkat \
    --setup_file prediction/setup.py \
    --requirements_file prediction/requirements.txt \
