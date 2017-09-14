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
from urlparse import urlparse

# Serice account credentials
#if on google cloud, can get credentials directly.

try:
    credentials = GoogleCredentials.get_application_default()
except:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json"

def process_args():
    parser = argparse.ArgumentParser(description='Create document for dataflow job.')
    parser.add_argument('-input_dir', help='Google cloud storage path for input videos samples.',default="gs://api-project-773889352370-testing/Hummingbirds/")
    parser.add_argument('-limit', help='Total number of videos',default=None,type=int)
    args, _ = parser.parse_known_args()
    return args

class Organizer:
    def __init__(self,args):

        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        self.parsed = urlparse(args.input_dir)

        #parse gcp path
        self.bucket = storage_client.get_bucket(self.parsed.hostname)
        vids=self.bucket.list_blobs(prefix=self.parsed.path[1:])

        #video list
        self.video_list=[]

        #first position is always folder containing videos
        is_first=True

        for vid in vids:
            if is_first:
                is_first=False
                continue
            self.video_list.append("gs://" + self.bucket.name +"/"+ str(vid.name))

        #Limit total number of videos if testing
        if args.limit:
            self.video_list=self.video_list[0:limit]
        
        print(self.video_list)

    def WriteCsv(self):

        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')

        with open(fn,"wb") as f:
            writer=csv.writer(f)
            for row in self.video_list:
                writer.writerow([row])

        #write to google cloud
        blob=self.bucket.blob("DataFlow/manifest.csv")
        blob.upload_from_filename(fn)

if __name__ == "__main__":
    args = process_args()
    p=Organizer(args)
    p.WriteCsv()
