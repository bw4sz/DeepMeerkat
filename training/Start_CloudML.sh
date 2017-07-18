#! /bin/bash 

#TODO startup script metadata and kill instance when you are done.
gcloud compute instances create cloudml
    --image-family=container-vm
    --image-project=google-containers
    --boot-disk-size "40"
    --service-account "773889352370-compute@developer.gserviceaccount.com"
    --scopes "https://www.googleapis.com/auth/cloud-platform" 
    --metadata-from-file startup-script=Training.sh 
 
#gcloud -q compute instances delete cloudml
gcloud -q compute instances delete cloudml
