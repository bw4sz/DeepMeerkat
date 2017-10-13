# this should be your array of image data dictionaries. 
# Don't forget that you'll want to separate your training and testing data.

from tfrecords.create_tfrecords import create
import glob
import json
import os

paths = glob.glob("/Users/Ben/Dropbox/GoogleCloud/Detection/Positives/annotations/*.json")

dataset=[]

#The json does not have full path

os.getcwd()

# read in json
for path in paths:
    js = open(path).read()
    data = json.loads(js)
    #append the full path
    data['filename']= '/Users/ben/Dropbox/GoogleCloud/Detection/Positives/' + data['filename']
    #add an ID path
    data['id']=0
    dataset.append(data)

#Split into training and eval 80-20
sp=int(len(dataset)*.8)

training=dataset[:sp]
evaluation=dataset[sp:]

print("{}  training images".format(len(training)))
print("{}  evaluation images".format(len(evaluation)))
      
#Convert training
failed_images = create(
    dataset=training,
  dataset_name="train",
  output_directory="/Users/Ben/Dropbox/GoogleCloud/Detection/tfrecords",
  num_shards=10,
  num_threads=5
)

print("%d images failed." % (len(failed_images),))
for image_data in failed_images:
    print("Image %s: %s" % (image_data['filename'], image_data['error_msg']))
    
#convert evaluation
failed_images = create(
    dataset=evaluation,
  dataset_name="eval",
  output_directory="/Users/Ben/Dropbox/GoogleCloud/Detection/tfrecords",
  num_shards=10,
  num_threads=5
)

print("%d images failed." % (len(failed_images),))
for image_data in failed_images:
    print("Image %s: %s" % (image_data['filename'], image_data['error_msg']))