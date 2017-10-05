# DeepMeerkat
Background subtraction and image classification for stationary cameras in ecological videos.

# Installation

DeepMeerkat has been tested on Windows 10, OSX Sierra 10.12.16, and Linux (Debian)

* Installers for a GUI interface are available for Mac and Windows

![GUI](https://www.dropbox.com/s/7qg2w3spbawnaa0/DeepMeerkatFrontScreen.png)

# Command Line

Command line arguments can be found [here](https://github.com/bw4sz/DeepMeerkat/blob/master/DeepMeerkat/CommandArgs.py)

# Use

1. Retrain a neural network for a two class classification. DeepMeerkat requires a tensorflow model in the SavedModel format. These classes correspond to "positive" and "negative". Positive are frames that the user is interested in reviewing, negative are frames that can be ignored. I suggest following this (tutorial)[https://cloud.google.com/blog/big-data/2016/12/how-to-classify-images-with-tensorflow-using-google-cloud-machine-learning-and-cloud-dataflow]. A starter (scripts)[https://github.com/bw4sz/DeepMeerkat/blob/master/training/Training.sh] can be found under the /Training directory

2. Run DeepMeerkat locally after supplying the path to the SavedModel in the advanced settings (GUI) or --path_to_model from command line.

DeepMeerkat was supported by a Open Data Fellow from [Segment](https://open.segment.com/fellowship)
