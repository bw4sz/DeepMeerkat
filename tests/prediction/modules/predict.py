import argparse
import json
import logging
import os
import csv

import apache_beam as beam
from DeepMeerkat import MotionMeerkat
  
class PredictDoFn(beam.DoFn):
  def process(self,element):
    MM=MotionMeerkat()    
    MM.process_args() 
    
    #Assign input from DataFlow/manifest
    MM.input=element
    MM.run()

def run(argv=None):
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', default="gs://api-project-773889352370-testing/DataFlow/manifest.csv",
                      help='Input file to process.')
  known_args, pipeline_args = parser.parse_known_args(argv)
  
  p = beam.Pipeline(argv=pipeline_args)
  
  vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run MotionMeerkat' >> beam.ParDo(PredictDoFn()))
  
  logging.getLogger().setLevel(logging.INFO)
  p.run()