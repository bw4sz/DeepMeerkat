from __future__ import absolute_import

'''
Create documents for parallel processing of videos using cloud dataflow
'''

import os
from google.cloud import storage
from oauth2client.client import GoogleCredentials
import random
import csv
import tempfile
import argparse
    
# Serice account credentials
#needs to check where I am running, if on google cloud, can get credentials directly.
try:
    credentials = GoogleCredentials.get_application_default()
except:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json"

def process_args():
    parser = argparse.ArgumentParser(description='Create document for dataflow job.')
    parser.add_argument('--input_dir', help='Google cloud storage path for input videos samples.',default="gs://api-project-773889352370-testing/Clips/")
    parser.add_argument('--limit', help='Total number of videos',default=None)
    args, _ = parser.parse_known_args()
    return args    

class Organizer:
    def __init__(self,args):
        
        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        self.parsed = urlparse(self.image_path)
        
        #parse gcp path
        self.bucket = self.storage_client.get_bucket(self.parsed.hostname)    
        vids=self.bucket.list_blobs(prefix=self.parsed.path[1:])
        
        #image list
        self.video_list=[]
        for vid in vids:
            self.video_list.append("gs://" + self.bucket.name +"/"+ str(vid.name))
                
        #if no ceiling, process all arguments
        if not limit:
            limit=len(jpgs)
            
        for x in vids[0:limit]:
            jpg = self.vision_client.image(source_uri=x) 
            self.videos_to_run.append(jpg) 
    #positives
    positives_folder_name=positives.split("/")[3:]
    iterator=self.bucket.list_blobs(prefix="/".join(positives_folder_name))        
    
    self.positives_files=[]        
    for page in iterator.pages:
        for f in page:
            self.positives_files.append("gs://" + f.bucket.name + "/" + f.name)
        
    print( "Found %d results" %(len( self.positives_files)))  
                    
    def WriteCsv(self):

        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(handle,"w",newline='') as f:
            writer=csv.writer(f)
            for eachrow in  self.positives_training:
                writer.writerow([eachrow,"positive"])
        
        #write to google cloud
        blob=self.bucket.blob("DataFlow/manifest.csv")
        blob.upload_from_filename(fn)
                
if __name__ == "__main__":
    args = process_args()
    p=Organizer(args)
    p.WriteCsv()