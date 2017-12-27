export BUCKET_NAME=your-bucket-name
export JOB_NAME="mnist_mlp_train_$(date +%Y%m%d_%H%M%S)"
export JOB_DIR=gs://$BUCKET_NAME/$JOB_NAME
export REGION=us-east1

gcloud ml-engine jobs submit training $JOB_NAME \
    --job-dir $JOB_DIR \
    --runtime-version 1.0 \
    --module-name trainer.mnist_mlp \
    --package-path ./trainer \
    --region $REGION \
    -- \
    --train-file gs://$BUCKET_NAME/data/mnist.pkl