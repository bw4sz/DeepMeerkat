import argparse
import json
import logging
import os
import csv

import apache_beam as beam
import DeepMeerkat
  
class PredictDoFn(beam.DoFn):
  def process(self,element):
      DeepMeerkat.MotionMeerkat(element)
    return None

def run(argv=None):
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', dest='input', required=True,
                      help='Input file to process.')
  parser.add_argument('--output', dest='output', required=True,
                      help='Output file to write results to.')
  parser.add_argument('--source', dest='source', default="gs://api-project-773889352370-testing/Dataflow/",
                      help='Data source location.')
  known_args, pipeline_args = parser.parse_known_args(argv)
  
  _ = (p | 'Read input' >> read_input_source
       | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Run MotionMeerkat' >> beam.ParDo(PredictDoFn()))

  logging.getLogger().setLevel(logging.INFO)
  p.run()