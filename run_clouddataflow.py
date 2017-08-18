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
  def __init__(self,argv):
    #capture any command line arguments passed to dataflow that belong to DeepMeerkat
    self.argv=argv
    
  def process(self,element):

    import csv
    from google.cloud import storage
    from DeepMeerkat import DeepMeerkat
    from urlparse import urlparse
    import os
    import google.auth
    import logging

    DM=DeepMeerkat.DeepMeerkat()

    logging.info(os.getcwd())
    logging.info(element)

    #try adding credentials?
    #set credentials, inherent from worker
    credentials, project = google.auth.default()

    #download element locally
    parsed = urlparse(element[0])
    logging.info(parsed)

    #parse gcp path
    storage_client=storage.Client(credentials=credentials)
    bucket = storage_client.get_bucket(parsed.hostname)
    blob=storage.Blob(parsed.path[1:],bucket)

    #store local path
    local_path="/tmp/" + parsed.path.split("/")[-1]

    logging.info('local path: ' + local_path)
    with open(local_path, 'wb') as file_obj:
      blob.download_to_file(file_obj)
    
    logging.info("Check local path exists: " + str(os.path.exists(local_path)))

    #Assign input from DataFlow/manifest
    DM.process_args(video=local_path,argv=self.argv)
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

      #create GCS path and strip exntension for the folder name
      folder=os.path.splitext(parsed.path.split("/")[-1])[0]
      path="DeepMeerkat/" + folder  + "/" + frame.split("/")[-1]
      
      #upload to gcs
      blob=storage.Blob(path,bucket)
      blob.upload_from_filename(frame)
      
      #delete frame
      os.remove(frame)

def run():
  import argparse
  import os
  import apache_beam as beam
  import csv
  import logging
  import google.auth

  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', default="gs://api-project-773889352370-testing/DataFlow/manifest.csv",
                      help='Input file to process.')
  parser.add_argument('--authtoken', default="/Users/Ben/Dropbox/Google/MeerkatReader-9fbf10d1e30c.json",
                      help='Input file to process.')
  known_args, pipeline_args = parser.parse_known_args()
  
  #expose args
  print("Known args: " + str(known_args))
  print("Pipe args: " + str(pipeline_args))
  
  #set credentials, inherent from worker
  try:
      credentials, project = google.auth.default()
  except:
      os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = known_args.authtoken
      credentials, project = google.auth.default()

  p = beam.Pipeline(argv=pipeline_args)

  vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run DeepMeerkat' >> beam.ParDo(PredictDoFn(pipeline_args)))

  logging.getLogger().setLevel(logging.INFO)
  p.run()

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
