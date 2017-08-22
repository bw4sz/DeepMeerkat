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
import sys
if sys.version_info >= (3, 0):
    from urllib import urlparse
else:
    from urlparse import urlparse
import argparse

# Serice account credentials
#If on google cloud, can get credentials directly.
try:
    credentials = GoogleCredentials.get_application_default()
except:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json"

def process_args():
    parser = argparse.ArgumentParser(description='Runs Flowers Sample E2E pipeline.')
    parser.add_argument('--train_positives', help='Google cloud storage path for positive samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Training/Positives/")
    parser.add_argument('--train_negatives', help='Google cloud storage path for negatives samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Training/Negatives/")
    parser.add_argument('--test_positives', help='Google cloud storage path for positive samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Testing/Positives/")
    parser.add_argument('--test_negatives', help='Google cloud storage path for negatives samples.',default="gs://api-project-773889352370-ml/Hummingbirds/Testing/Negatives/")
    parser.add_argument('--debug', help='Debug dataset, only write a small portion to reduce run time',action="store_true")    
    
    args, _ = parser.parse_known_args()
    return args    

class Organizer:
    def __init__(self,train_positives,train_negatives,test_positives,test_negatives,debug):
        
        #set testing switch
        self.debug=debug
        
        credentials = GoogleCredentials.get_application_default()
        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        
        #parse names
        bucket_name=positives.split("/")[2]
    
        #open bucket
        self.bucket = storage_client.get_bucket(bucket_name)
        
        ##TRAINING
        #positives
        train_positives_folder_name=train_positives.split("/")[3:]
        iterator=self.bucket.list_blobs(prefix="/".join(train_positives_folder_name))        
        
        self.positives_files=[]        
        for page in iterator.pages:
            print('    Page number: %d' % (iterator.page_number,))
            print('  Items in page: %d' % (page.num_items,))
            print('     First item: %r' % (next(page),))
            print('Items remaining: %d' % (page.remaining,))
            print('Next page token: %s' % (iterator.next_page_token,))        
            for f in page:
                self.positives_files.append("gs://" + f.bucket.name + "/" + f.name)
            
        print( "Found %d results" %(len( self.train_positives_files)))  
        
        #negatives
        train_negatives_folder_name=train_negatives.split("/")[3:]
        iterator=self.bucket.list_blobs(prefix="/".join(train_negatives_folder_name))        
        
        self.train_negatives_files=[]        
        for page in iterator.pages:
            print('    Page number: %d' % (iterator.page_number,))
            print('  Items in page: %d' % (page.num_items,))
            print('     First item: %r' % (next(page),))
            print('Items remaining: %d' % (page.remaining,))
            print('Next page token: %s' % (iterator.next_page_token,))        
            for f in page:
                self.train_negatives_files.append("gs://" + f.bucket.name + "/" + f.name)
            
        print( "Found %d results" % (len( self.train_negatives_files)))          
        
    ##Testing - comes from a different bucket
    #positives
    test_positives_folder_name=test_positives.split("/")[3:]
    iterator=self.bucket.list_blobs(prefix="/".join(test_positives_folder_name))        
    
    self.positives_files=[]        
    for page in iterator.pages:
        print('    Page number: %d' % (iterator.page_number,))
        print('  Items in page: %d' % (page.num_items,))
        print('     First item: %r' % (next(page),))
        print('Items remaining: %d' % (page.remaining,))
        print('Next page token: %s' % (iterator.next_page_token,))        
        for f in page:
            self.test_positives_files.append("gs://" + f.bucket.name + "/" + f.name)
        
    print( "Found %d results" %(len( self.test_positives_files)))  
    
    #negatives
    test_negatives_folder_name=test_negatives.split("/")[3:]
    iterator=self.bucket.list_blobs(prefix="/".join(test_negatives_folder_name))        
    
    self.negatives_files=[]        
    for page in iterator.pages:
        print('    Page number: %d' % (iterator.page_number,))
        print('  Items in page: %d' % (page.num_items,))
        print('     First item: %r' % (next(page),))
        print('Items remaining: %d' % (page.remaining,))
        print('Next page token: %s' % (iterator.next_page_token,))        
        for f in page:
            self.test_negatives_files.append("gs://" + f.bucket.name + "/" + f.name)
        
    print( "Found %d results" % (len( self.test_negatives_files)))    
    
    def write_data(self):
        
        ##Training
        
        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(fn,"wb") as f:
            writer=csv.writer(f)
            for eachrow in  self.train_positives_files:
                writer.writerow([str(eachrow),"positive"])
            for eachrow in  self.train_negatives_files:
                writer.writerow([str(eachrow),"negative"])
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/trainingdata.csv")
        blob.upload_from_filename(fn)
        
        ##Testing
        
        #Write to temp then send to google cloud
        handle, fn = tempfile.mkstemp(suffix='.csv')
        
        with open(fn,"wb") as f:
            writer=csv.writer(f)
            for eachrow in  self.test_positives_files:
                writer.writerow([str(eachrow),"positive"])
            for eachrow in  self.test_negatives_files:
                writer.writerow([str(eachrow),"negative"])
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/testingdata.csv")
        blob.upload_from_filename(fn)    
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/holdoutdata.csv")
        blob.upload_from_filename(fn)    

        #write dict file 
        handle, fn = tempfile.mkstemp(suffix='.txt')        
        with open(fn,"wb") as f:
            f.write("positive"+"\n")
            f.write("negative")
            f.close()
        
        #write to google cloud
        blob=self.bucket.blob("Hummingbirds/dict.txt")
        blob.upload_from_filename(fn)               
        
if __name__ == "__main__":
    args = process_args()
    p=Organizer(train_positives=args.train_positives, train_negatives=args.train_negatives,test_positives=args.test_positives, 
                test_negatives=args.test_negatives,debug=args.debug)
    p.divide_data(prop=args.prop,prop_out=args.prop_out)
    p.write_data()