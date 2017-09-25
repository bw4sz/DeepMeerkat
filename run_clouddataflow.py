import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from urlparse import urlparse
  
class PredictDoFn(beam.DoFn):
  def __init__(self,argv):
    #capture any command line arguments passed to dataflow that belong to DeepMeerkat
    self.argv=argv
  
  def process(self,element):
    ##The namespaces inside of clouddataflow workers is not inherited
    import csv
    from DeepMeerkat import DeepMeerkat
    from urlparse import urlparse
    import os
    import subprocess
    import logging

    DM=DeepMeerkat.DeepMeerkat()

    #Download tensorflow model, if it does not exist
    if not os.path.exists("/tmp/model/"):
      cmd=["gsutil","cp","-r","gs://api-project-773889352370-ml/DeepMeerkat/DeepMeerkat_20170924_105144/model","/tmp/"]
      subprocess.call(cmd)
      
    logging.info(os.getcwd())
    logging.info(element)
    
    #download element locally
    parsed = urlparse(element[0])
    logging.info(parsed)

    #add in folder name and video name
    local_path="/tmp/"+"/".join(parsed.path.split("/")[-2:])

    cmd=["gsutil","cp",element[0],local_path]
    subprocess.call(cmd)    
        
    print("Local path: " + str(local_path))
    if os.path.exists(local_path):
      logging.info("Local path exists")
    else:
      raise("Local path does not exist")
    
    #Assign input from DataFlow/manifest.
    #default args
    DM.process_args(argv=self.argv)
    #file queue
    DM.create_queue(video=local_path)
    #specify output location
    DM.args.output="/tmp/Frames"
    DM.args.path_to_model = "/tmp/model/"

    #Run DeepMeerkat
    for vid in DM.queue:
      DM.run(vid=vid)
    
    #Set output folder
    output_path=parsed.scheme+"://"+parsed.netloc+"/DeepMeerkat/"     

    cmd=["gsutil","-m","cp","-r","/tmp/Frames/*",output_path]
    subprocess.call(cmd)
    
    #clean out /tmp
    subprocess.call(["rm",local_path])
    subprocess.call(["rm","-rf","/tmp/Frames/"])
    print("End")
    
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
  
  #expose args
  print("Known args: " + str(known_args))
  print("Pipe args: " + str(pipeline_args))

  p = beam.Pipeline(argv=pipeline_args)

  vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run DeepMeerkat' >> beam.ParDo(PredictDoFn(pipeline_args)))

  logging.getLogger().setLevel(logging.INFO)
  p.run()

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
