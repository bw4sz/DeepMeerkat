#! /bin/bash 

#TODO startup script metadata  
gcloud compute instances create cloudml
    --image-family=container-vm
    --image-project=google-containers
    --boot-disk-size "40"
    --service-account "773889352370-compute@developer.gserviceaccount.com"
    --scopes "https://www.googleapis.com/auth/cloud-platform" 
    --start-from-metadata Training.sh
    
#kill instance when you are done.
gcloud compute instances delete cloudml

#Refresh the summary csv files
gsutil cp -r gs://api-project-773889352370-ml/Hummingbirds/Prediction/Summary/* C:/Users/Ben/Dropbox/GoogleCloud/Summary/

#Parse csv 
Rscript -e "knitr::knit('Training.Rmd')"