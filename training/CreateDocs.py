from __future__ import absolute_import

'''
Create documents for training a tensorflow model training dataset on google cloud machine learning engine.
This script is built for a two class training dataset, images with desired objects (positives) and images with ignored objects (negatives)
see:
http://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow
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
    parser = argparse.ArgumentParser(description='Runs Flowers Sample E2E pipeline.')
    parser.add_argument('--positives', help='Google cloud storage path for positive samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Positives/")
    parser.add_argument('--negatives', help='Google cloud storage path for negatives samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Negatives/")
    parser.add_argument('--prop', help='Proportion of training data',default=0.7,type=float)
    parser.add_argument('--prop_out', help='Proportion of testing data to hold out of sample',default=0.1,type=float)    
    parser.add_argument('--debug', help='Debug dataset, only write a small portion to reduce run time',action="store_true")    
    
    args, _ = parser.parse_known_args()
    return args    

class Organizer:
    def __init__(self,positives,negatives,debug):
        
        #set testing switch
        self.debug=debug
        
        credentials = GoogleCredentials.get_application_default()
        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        
        #parse names
        bucket_name=positives.split("/")[2]
    
        #open bucket
        self.bucket = storage_client.get_bucket(bucket_name)
        
        #positives
        positives_folder_name=positives.split("/")[3:]
        iterator=self.bucket.list_blobs(prefix="/".join(positives_folder_name))        
        
        self.positives_files=[]        
        for page in iterator.pages:
            print('    Page number: %d' % (iterator.page_number,))
            print('  Items in page: %d' % (page.num_items,))
            print('     First item: %r' % (next(page),))
            print('Items remaining: %d' % (page.remaining,))
            print('Next page token: %s' % (iterator.next_page_token,))        
            for f in page:
                self.positives_files.append("gs://" + f.bucket.name + "/" + f.name)
            
        print( "Found %d results" %(len( self.positives_files)))  
        
        #negatives
        #positives
        negatives_folder_name=negatives.split("/")[3:]
        iterator=self.bucket.list_blobs(prefix="/".join(negatives_folder_name))        
        
        self.negatives_files=[]        
        for page in iterator.pages:
            print('    Page number: %d' % (iterator.page_number,))
            print('  Items in page: %d' % (page.num_items,))
            print('     First item: %r' % (next(page),))
            print('Items remaining: %d' % (page.remaining,))
            print('Next page token: %s' % (iterator.next_page_token,))        
            for f in page:
                self.negatives_files.append("gs://" + f.bucket.name + "/" + f.name)
            
        print( "Found %d results" % (len( self.negatives_files)))  
        
    def divide_data(self,prop,prop_out):
        
        #Shuffle positive datasets and divide
        positives_random=self.positives_files
        random.shuffle(positives_random)
        
        self.positives_training=positives_random[:int(len(positives_random)*prop)]
        self.positives_testing=positives_random[int(len(positives_random)*prop):]

        #Shuffle negatives datasets and divide
        negatives_random=self.negatives_files
        random.shuffle(negatives_random)
        
        self.negatives_training=negatives_random[:int(len(negatives_random)*prop)]
        self.negatives_testing=negatives_random[int(len(negatives_random)*prop):]
        
        #split testing data into in sample and out of sample
        self.negatives_holdout=self.negatives_testing[:int(len(self.negatives_testing)*prop_out)]
        self.positives_holdout=self.positives_testing[:int(len(self.positives_testing)*prop_out)]

        self.negatives_testing=self.negatives_testing[int(len(self.negatives_testing)*prop_out):]
        self.positives_testing=self.positives_testing[int(len(self.positives_testing)*prop_out):]
                
        #debug model, only write a tiny dataset
        if self.debug:
            self.positives_training=self.positives_training[0:50]
            self.positives_testing=self.positives_testing[0:10]
            self.negatives_training=self.negatives_training[0:50]
            self.negatives_testing=self.negatives_training[0:10]
            
    def write_data(self):
        
        ##Training
        
        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(handle,"w",newline='') as f:
            writer=csv.writer(f)
            for eachrow in  self.positives_training:
                writer.writerow([eachrow,"positive"])
            for eachrow in  self.negatives_training:
                writer.writerow([eachrow,"negative"])
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/trainingdata.csv")
        blob.upload_from_filename(fn)
        
        ##Testing
        
        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(handle,"w",newline='') as f:
            writer=csv.writer(f)
            for eachrow in  self.positives_testing:
                writer.writerow([eachrow,"positive"])
            for eachrow in  self.negatives_testing:
                writer.writerow([eachrow,"negative"])
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/testingdata.csv")
        blob.upload_from_filename(fn)    

        ##Holdout
        
        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(handle,"w",newline='') as f:
            writer=csv.writer(f)
            for eachrow in  self.positives_testing:
                writer.writerow([eachrow,"positive"])
            for eachrow in  self.negatives_testing:
                writer.writerow([eachrow,"negative"])
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/holdoutdata.csv")
        blob.upload_from_filename(fn)    

        #write dict file 
        handle, fn = tempfile.mkstemp(suffix='.txt')        
        with open(handle,"w",newline="") as f:
            f.write("positive"+"\n")
            f.write("negative")
            f.close()
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/dict.txt")
        blob.upload_from_filename(fn)               
        
if __name__ == "__main__":
    args = process_args()
    p=Organizer(positives=args.positives, negatives=args.negatives,debug=args.debug)
    p.divide_data(prop=args.prop,prop_out=args.prop_out)
    p.write_data()