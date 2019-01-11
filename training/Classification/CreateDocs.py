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
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json"

class Organizer:
    def __init__(self,args):
        
        credentials = GoogleCredentials.get_application_default()
        
        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        
        #parse names
        parsed_url = urlparse(args.DATA_PATH)
        bucket_name= "://".join([parsed_url.scheme, parsed_url.netloc])
            
        #open bucket
        self.bucket = storage_client.get_bucket(parsed_url.netloc)
        
        #Set folder names
        self.data_folder =  parsed_url.path.split("/")[-1] 
        train_positives_folder_name = self.data_folder + "/Training/Positives/"
        train_negatives_folder_name =  self.data_folder + "/Training/Negatives/"
        test_positives_folder_name = self.data_folder  + "/Testing/Positives/"
        test_negatives_folder_name = self.data_folder + "/Testing/Negatives/"
        
        #### Positives
        iterator = self.bucket.list_blobs(prefix =  train_positives_folder_name)     
        
        self.train_positives_files = [ ]        
        for item in iterator:
            self.train_positives_files.append("gs://" + item.bucket.name + "/" + item.name)
            
        print( "Positive training samples: %d" % (len( self.train_positives_files)))  
        
        #### Negatives
        iterator = self.bucket.list_blobs(prefix = train_negatives_folder_name)       
        
        self.train_negatives_files = [ ]        
        for f in iterator:
            self.train_negatives_files.append("gs://" + f.bucket.name + "/" + f.name)
                    
        #shuffle negatives and take a sample equal to the size of the positives
        random.shuffle(self.train_negatives_files)
        
        #add the rest of the files to testing
        #add_to_negative_train=self.train_negatives_files[len(self.train_positives_files):]
        
        #cut the file to match positives
        self.train_negatives_files = self.train_negatives_files[ : len(self.train_positives_files)]
        print("Negative Training Samples: %d" % (len(self.train_negatives_files)))          
        
        ##Testing 
        #Positives
        iterator=self.bucket.list_blobs(prefix = test_positives_folder_name)        
        
        self.test_positives_files = [ ]        
        for f in iterator:     
            self.test_positives_files.append("gs://" + f.bucket.name + "/" + f.name)
        print("Positive Testing samples: %d" % (len(self.test_positives_files)))  
        
        #negatives
        iterator = self.bucket.list_blobs(prefix = test_negatives_folder_name)
        
        self.test_negatives_files = [ ]        
        for f in iterator:   
                self.test_negatives_files.append("gs://" + f.bucket.name + "/" + f.name)
            
        #add in the negatives
        #self.test_negatives_files=add_to_negative_train + self.test_negatives_files
        print("Negative testing samples: %d" % (len(self.test_negatives_files)))    
        
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
        blob=self.bucket.blob(self.data_folder + "/trainingdata.csv")
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
        blob=self.bucket.blob(self.data_folder + "/testingdata.csv")
        blob.upload_from_filename(fn)    

        #write dict file 
        handle, fn = tempfile.mkstemp(suffix='.txt')        
        with open(fn,"wb") as f:
            f.write("positive"+"\n")
            f.write("negative")
            f.close()
        
        #write to google cloud
        blob=self.bucket.blob(self.data_folder + "/dict.txt")
        blob.upload_from_filename(fn)  
            
def process_args():
    parser = argparse.ArgumentParser(description='Runs Flowers Sample E2E pipeline.')
    parser.add_argument('--DATA_PATH', help='Google cloud storage path for data', default="gs://api-project-773889352370-ml/Hummingbirds/")
    parser.add_argument('--debug', help='Debug dataset, only write a small portion to reduce run time', action="store_true")    
    
    args, _ = parser.parse_known_args()
    return args                 
        
if __name__ == "__main__":
    print(__name__)
    args = process_args()
    print(args)
    p=Organizer(args)
    p.write_data()