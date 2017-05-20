#! /bin/bash 

#local
#Create docker container with local credentials if needed
#docker run -t -i -v C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json:/tmp/MeerkatReader-9fbf10d1e30c.json --name gcloud-config google/cloud-sdk gcloud auth activate-service-account 773889352370-compute@developer.gserviceaccount.com --key-file /tmp/MeerkatReader-9fbf10d1e30c.json --project api-project-773889352370
#docker run --rm -it --volumes-from gcloud-config gcr.io/api-project-773889352370/cloudmlengine

#get startup script info
#gcloud compute instances get-serial-port-output cloudml

#TODO startup script metadata  
gcloud compute instances create cloudml
    --image-family=container-vm
    --image-project=google-containers
    --boot-disk-size "40"
    --service-account "773889352370-compute@developer.gserviceaccount.com"
    --scopes "https://www.googleapis.com/auth/cloud-platform" 
    
#for the moment, ssh instance
gcloud compute ssh cloudml 
      
#kill instance when you are done.
gcloud compute instances delete cloudml
