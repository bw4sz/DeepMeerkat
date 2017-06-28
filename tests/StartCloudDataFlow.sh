#! /bin/bash 

PROJECT=$(gcloud config list project --format "value(core.project)")
BUCKET=gs://$PROJECT-testing

#copy most recent DeepMeerkat in version control from main directory
cp -r ../DeepMeerkat/ prediction/modules/

#generate manifest 
python prediction/createdoc.py

python prediction/run.py \
    --runner DataflowRunner \
    --project $PROJECT \
    --staging_location $BUCKET/staging \
    --temp_location $BUCKET/temp \
    --job_name $PROJECT-prediction-cs \
    --setup_file prediction/setup.py \
    --model $BUCKET/model \
    --source cs \
    --input $BUCKET/input/images.txt \
    --output $BUCKET/output/predict