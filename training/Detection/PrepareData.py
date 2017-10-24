import glob
import json
import os
import tensorflow as tf
from GenerateTFRecords import create_tf_example
paths = glob.glob("/Users/Ben/Dropbox/GoogleCloud/Detection/images/training/annotations/*.json")

dataset=[]

#The json does not have full path

os.getcwd()

# read in json
for path in paths:
    js = open(path).read()
    data = json.loads(js)
    
    #append the full path
    data['filename']= '/Users/ben/Dropbox/GoogleCloud/Detection/images/training/' + data['filename']
    dataset.append(data)

#Split into training and eval 80-20
sp=int(len(dataset)*.8)

training=dataset[:sp]
evaluation=dataset[sp:]

print("{}  training images".format(len(training)))
print("{}  evaluation images".format(len(evaluation)))
      
#Convert training
writer = tf.python_io.TFRecordWriter("/Users/ben/Dropbox/GoogleCloud/Detection/tfrecords/train.record") #output path

for data in training:
    tf_example = create_tf_example(data)
    writer.write(tf_example.SerializeToString())

writer.close()
print('Successfully created the training TFRecords')

#Convert evaluation
writer = tf.python_io.TFRecordWriter("/Users/ben/Dropbox/GoogleCloud/Detection/tfrecords/eval.record") #output path
for data in evaluation:
    tf_example = create_tf_example(data)
    writer.write(tf_example.SerializeToString())

writer.close()
print('Successfully created the evaluation TFRecords')
