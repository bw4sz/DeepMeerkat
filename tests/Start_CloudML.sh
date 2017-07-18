#! /bin/bash 

#TODO startup script metadata  
gcloud compute instances create cloudml
    --image-family=container-vm
    --image-project=google-containers
    --boot-disk-size "40"
    --service-account "773889352370-compute@developer.gserviceaccount.com"
    --scopes "https://www.googleapis.com/auth/cloud-platform" 
    --start-from-metadata StartCloudDataFlow.sh
    
#kill instance when you are done.
gcloud -q compute instances delete cloudml
