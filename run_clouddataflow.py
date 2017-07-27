import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from DeepMeerkat import DeepMeerkat

class PredictDoFn(beam.DoFn):
  
  def process(self,element):
    DM=DeepMeerkat.DeepMeerkat()  
    #replace input with element
    #Assign input from DataFlow/manifest    
    #DM.process_args(video=element[0])   
    DM.process_args()       
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
