import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from DeepMeerkat import DeepMeerkat
from oauth2client.client import GoogleCredentials
from urlparse import urlparse
from google.cloud import storage

class PredictDoFn(beam.DoFn):
  
  def process(self,element):
    DM=DeepMeerkat.DeepMeerkat()  

    #download element locally
    credentials = GoogleCredentials.get_application_default()
    parsed = urlparse(element[0])
  
    #parse gcp path
    storage_client=storage.Client()
    bucket = storage_client.get_bucket(parsed.hostname)
    
    blob=Blob(element[0],bucket)
    local_path="/tmp/"+self.name
    
    with open(local_path, 'wb') as file_obj:
      blob.download_to_file(file_obj)
    
    #Assign input from DataFlow/manifest
    DM.process_args(video=local_path)   
    print(os.getcwd())
    print(element)    
    DM.run()

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', default="gs://api-project-773889352370-testing/DataFlow/manifest.csv",
                      help='Input file to process.')
  known_args, pipeline_args = parser.parse_known_args()
    
  p = beam.Pipeline(argv=pipeline_args)
  
  vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run DeepMeerkat' >> beam.ParDo(PredictDoFn()))
  
  logging.getLogger().setLevel(logging.INFO)
  p.run()
  
if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
