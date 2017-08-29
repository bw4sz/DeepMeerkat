import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from urlparse import urlparse
from google.cloud import storage

  
class PredictDoFn(beam.DoFn):
  def __init__(self,argv):
    #capture any command line arguments passed to dataflow that belong to DeepMeerkat
    self.argv=argv
  
  def process(self,element):
    ##The namespaces inside of clouddataflow workers is not inherited
    import csv
    from google.cloud import storage
    from DeepMeerkat import DeepMeerkat
    from urlparse import urlparse
    import os
    import google.auth
    import subprocess
    import logging

    DM=DeepMeerkat.DeepMeerkat()

    logging.info(os.getcwd())
    logging.info(element)

    #set credentials, inherent from worker
    credentials, project = google.auth.default()

    #download element locally
    parsed = urlparse(element[0])
    logging.info(parsed)

    cmd=["gsutil","cp",element[0],"/tmp/"]
    subprocess.call(cmd)    
    
    logging.info("Check local path exists: " + str(os.path.exists(local_path)))

    #Assign input from DataFlow/manifest
    DM.process_args(video=local_path,argv=self.argv)
    DM.args.output="/tmp/Frames"

    #Run DeepMeerkat
    DM.run()
    
    #Set output folder
    folder=os.path.splitext(parsed.path.split("/")[-1])[0]
    output_path=parsed.scheme+"://"+parsed.netloc+"DeepMeerkat/"+ folder     

    cmd=["gsutil","cp","/tmp/Frames/*",output_path]
    subprocess.call(cmd)
    
    #clean out /tmp
    subprocess.call("rm -rf /tmp/Frames/*")
    
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
       #| ("Read file" >> beam.FlatMap(read_file))       
       | 'Run DeepMeerkat' >> beam.ParDo(PredictDoFn(pipeline_args)))

  logging.getLogger().setLevel(logging.INFO)
  p.run()

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
