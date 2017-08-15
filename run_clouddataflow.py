import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from urlparse import urlparse
from google.cloud import storage

##The namespaces inside of clouddataflow workers is not inherited , 
##Please see https://cloud.google.com/dataflow/faq#how-do-i-handle-nameerrors, better to write ugly import statements then to miss a namespace

class PredictDoFn(beam.DoFn):
  def process(self,element):
    
    import csv
    import google.cloud.storage as storage
    from DeepMeerkat import DeepMeerkat
    from urlparse import urlparse
    
    DM=DeepMeerkat.DeepMeerkat()

    print(os.getcwd())
    print(element)

    #download element locally
    parsed = urlparse(element[0])

    #parse gcp path
    storage_client=storage.Client()
    bucket = storage_client.get_bucket(parsed.hostname)
    blob=storage.Blob(parsed.path[1:],bucket)

    #store local path
    local_path="/tmp/" + parsed.path.split("/")[-1]

    print('local path: ' + local_path)
    with open(local_path, 'wb') as file_obj:
      blob.download_to_file(file_obj)

    print("Downloaded" + local_path)

    #Assign input from DataFlow/manifest
    DM.process_args(video=local_path)
    DM.args.output="Frames"

    #Run DeepMeerkat
    DM.run()

    #upload back to GCS
    found_frames=[]
    for (root, dirs, files) in os.walk("Frames/"):
      for files in files:
        fileupper=files.upper()
        if fileupper.endswith((".JPG")):
          found_frames.append(os.path.join(root, files))

    for frame in found_frames:

      #create GCS path
      path="DeepMeerkat/" + parsed.path.split("/")[-1] + "/" + frame.split("/")[-1]
      blob=storage.Blob(path,bucket)
      blob.upload_from_filename(frame)

def run():
  import argparse
  import os
  import apache_beam as beam
  import csv
  import logging
  
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', default="gs://api-project-773889352370-testing/DataFlow/manifest.csv",
                      help='Input file to process.')
  parser.add_argument('--authtoken', default="/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json",
                      help='Input file to process.')
  known_args, pipeline_args = parser.parse_known_args()

  #set credentials
  os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = known_args.authtoken

  p = beam.Pipeline(argv=pipeline_args)

  vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run DeepMeerkat' >> beam.ParDo(PredictDoFn()))

  logging.getLogger().setLevel(logging.INFO)
  p.run()

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
