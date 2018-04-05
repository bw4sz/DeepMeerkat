# DeepMeerkat
Background subtraction and image classification for stationary cameras in ecological videos.
![](https://github.com/bw4sz/DeepMeerkat/blob/master/images/Hummingbird.png)

DeepMeerkat was supported by a Open Data Fellow from [Segment](https://open.segment.com/fellowship)

# Installation

DeepMeerkat has been tested on Windows 10, OSX Sierra 10.12.16, and Linux (Debian)

* Installers for a GUI interface are available for [Mac and Windows](benweinstein.weebly.com/deepmeerkat.html)
<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/DeepMeerkatFrontScreen.png" style=" width:50px ; height:50px " />

# Source Dependencies

If not running an installer, DeepMeerkat requires

* Tensorflow
* OpenCV

Please note that on Windows, Tensorflow requires python 3.5. On Mac >2.7 will work fine.

# Command Line

Command line arguments can be found [here](https://github.com/bw4sz/DeepMeerkat/blob/master/DeepMeerkat/CommandArgs.py)

# Training new models

0. Set up [google cloud environment](https://cloud.google.com/ml-engine/docs/getting-started-training-prediction). See the section "Set up and test your Cloud environment". You will need a operating GCP account, gsutil on your local machine, and the Cloud Machine Learning Engine API authenticated. While its greatly recommended to use google cloud, a slower local training example is in the 'local' [branch](https://github.com/bw4sz/DeepMeerkat/tree/local/training/Classification) of this repo.  

1. Retrain a neural network for a two class classification. DeepMeerkat requires a tensorflow model in the [SavedModel](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/saved_model/README.md) format. These classes correspond to "positive" and "negative". Positive are frames that the user is interested in reviewing, negative are frames that can be ignored. I suggest following this [tutorial](https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow). 

I provide example scripts that will help smooth out this process [scripts](https://github.com/bw4sz/DeepMeerkat/blob/master/training/Classification/Training.sh). This [example](https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow) from google is the inspiration for the approach. In future, I hope to provide a web platform to automate this process for local deployment.

## Training Example

0. Collect data

DeepMeerkat comes with a training mode to help automate this process. Select advanced settings -> training mode. This will return all frames of motion, regardless of predicted foreground/background probability.

Example output looks like this:

<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/trainingmode.png" style=" width:50px ; height:50px " />

From this output you need to score with the underscores. So 33_0.jpg is the first bounding box returned in frame 33. If there was two crops, there would also be 33_1.jpg. Don't score 33.jpg (for the moment). Put all the crops that have the target organism into into a folder called Positives. Put all the crops that do not have the target organism into a folder called Negatives. 

One thing to keep in mind is that the final dataset you will use needs to be balanced (# of Positives = # of Negatives). So while you can score every single negative in a video (there will be many), once you have roughly equal to the number of positives, just move to the next video.

Let's say I have a folder of positive images, and a folder of negative images. I need to 

1. Upload them into a google bucket
2. Create a .csv file that links the labels to the images.
3. Train a neural network using Google's tensorflow and Cloud Machine Learning Engine
4. *Ensure that dict.txt matches [here](https://github.com/bw4sz/DeepMeerkat/blob/master/training/Classification/dict.txt), don't change the order. DeepMeerkat (for the moment), has only been tested on a 2 class (foreground versus background) model.*

This can be done in [Training.sh](https://github.com/bw4sz/DeepMeerkat/blob/master/training/Classification/Training.sh). Your paths will no doubt be different than mine.

Let's start by declaring some variables. 

```
declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="DeepMeerkat"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"
```

Either upload or update your bucket with newly labeled images. Change "/Users/Ben/Dropbox/GoogleCloud/Training" to your correct paths.

```
#make sure paths are updated
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Positives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Positives
gsutil rsync -d /Users/Ben/Dropbox/GoogleCloud/Training/Negatives/ gs://api-project-773889352370-ml/Hummingbirds/Training/Negatives
```

Along with those images, you need a document specifying their path and label. Modify CreateDocs.py to point to your designed bucket and location.

#Create Docs
```
python CreateDocs.py
```

Its nice to know how many evaluation samples we have, again, your path will be different

```
#get eval set size
eval=$(gsutil cat gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv | wc -l)
```

############
#Train Model
############

Using Google's [pipeline](https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow) for retraining inception. Change "gs://api-project-773889352370-ml/Hummingbirds" to your bucket address.

```
python pipeline.py \
    --project ${PROJECT} \
    --cloud \
    --train_input_path gs://api-project-773889352370-ml/Hummingbirds/trainingdata.csv \
    --eval_input_path gs://api-project-773889352370-ml/Hummingbirds/testingdata.csv \
    --input_dict gs://api-project-773889352370-ml/Hummingbirds/dict.txt \
    --deploy_model_name "DeepMeerkat" \
    --gcs_bucket ${BUCKET} \
    --output_dir "${GCS_PATH}/"  \
    --eval_set_size  ${eval} 
```
You can check on the status of the cloud dataflow run, which should look like this:

<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/DataFlow.png" style=" width:50px ; height:50px " />

The pipeline will then take those features and fine tune the network using Cloud Machine Learning Engine

<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/Engine.png" style=" width:50px ; height:50px " />

This will result in a SavedModel object in your output_dir. 

<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/model.png" style=" width:50px ; height:50px " />

Now download that folder

```
gsutil cp -r ${GCS_PATH}/model .
```

When you run DeepMeerkat, this is the path you supply for your model. Either in the advanced settings (GUI) or --path_to_model from command line.

