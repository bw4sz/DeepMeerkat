import logging
import argparse
import json
import logging
import os
import csv
import apache_beam as beam
from urlparse import urlparse
from predict import images_to_json

class ConvertDoFn(beam.DoFn):
    def __init__(self,argv):
        #capture any command line arguments passed to dataflow that belong to DeepMeerkat
        self.argv=argv

    def process(self,element):
        ##The namespaces inside of clouddataflow workers is not inherited
        #import 
        
        #logging.info(os.getcwd()


class PredictDoFn(beam.DoFn):
    def __init__(self,argv):
        #capture any command line arguments passed to dataflow that belong to DeepMeerkat
        self.argv=argv

    def process(self,element):
        ##The namespaces inside of clouddataflow workers is not inherited
        #import 
        
        #logging.info(os.getcwd()

def run():
    import argparse
    import os
    import apache_beam as beam
    import csv
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', default="gs://api-project-773889352370-testing/DataFlow/prediction.csv",
                      help='Input file to process.')
    known_args, pipeline_args = parser.parse_known_args()

    #expose args
    print("Known args: " + str(known_args))
    print("Pipe args: " + str(pipeline_args))

    p = beam.Pipeline(argv=pipeline_args)

    vids = (p|'Read input' >> beam.io.ReadFromText(known_args.input)
          | 'Parse input' >> beam.Map(lambda line: csv.reader([line]).next())
       | 'Convert to JSON' >> beam.ParDo(ConvertDoFn(pipeline_args))
       | 'Serve Prediction' >> beam.ParDo(ServeDoFn(pipeline_args))

    logging.getLogger().setLevel(logging.INFO)
    p.run()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
