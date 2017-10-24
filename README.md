# DeepMeerkat
Background subtraction and image classification for stationary cameras in ecological videos.
![](https://github.com/bw4sz/DeepMeerkat/blob/master/images/Hummingbird.png)


# Installation

DeepMeerkat has been tested on Windows 10, OSX Sierra 10.12.16, and Linux (Debian)

* Installers for a GUI interface are available for [Mac and Windows](benweinstein.weebly.com/deepmeerkat.html)
<img src="https://github.com/bw4sz/DeepMeerkat/blob/master/images/DeepMeerkatFrontScreen.png" style=" width:50px ; height:50px " />

# Source Dependencies

If not running an installer, DeepMeerkat requires

* Tensorflow
* OpenCV

# Command Line

Command line arguments can be found [here](https://github.com/bw4sz/DeepMeerkat/blob/master/DeepMeerkat/CommandArgs.py)

# Use

1. Retrain a neural network for a two class classification. DeepMeerkat requires a tensorflow model in the SavedModel format. These classes correspond to "positive" and "negative". Positive are frames that the user is interested in reviewing, negative are frames that can be ignored. I suggest following this [tutorial](https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow). A starter [scripts](https://github.com/bw4sz/DeepMeerkat/blob/master/training/Training.sh) can be found under the /Training directory. In future, we hope to provide a web platform to automate this process for local deployment.

Training Example

Let's say I have a folder of positive images, and a folder of negative images. I need to 

1. Upload them into a google bucket
2. Create a .csv file that links the labels to the images.
3. Train a neural network using Google's tensorflow and Cloud Machine Learning Engine


Training.sh

Let's start by declaring some variables. 

```
declare -r PROJECT=$(gcloud config list project --format "value(core.project)")
declare -r BUCKET="gs://${PROJECT}-ml"
declare -r MODEL_NAME="DeepMeerkat"
declare -r JOB_ID="${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)"
declare -r GCS_PATH="${BUCKET}/${MODEL_NAME}/${JOB_ID}"
```

Either upload or update your bucket with newly labeled images.

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

Using Google's [pipeline](https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow) for retraining inception.

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

This will result in a SavedModel object in your output_dir. Now download that folder

```
gsutil cp -r ${GCS_PATH}/model .
```

When you run DeepMeerkat, this is the path you supply for your model. Either in the advanced settings (GUI) or --path_to_model from command line.

DeepMeerkat was supported by a Open Data Fellow from [Segment](https://open.segment.com/fellowship)
