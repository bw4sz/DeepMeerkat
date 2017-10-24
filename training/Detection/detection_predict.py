import numpy as np
import tensorflow as tf
from PIL import Image
import glob
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
import os
import datetime

# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
TEST_IMAGE_PATHS = glob.glob("/Users/Ben/Dropbox/GoogleCloud/Detection/images/validation/*.jpg")

# Size, in inches, of the output images. ?
IMAGE_SIZE = (6, 4)
NUM_CLASSES = 1

sess=tf.Session()
tf.saved_model.loader.load(sess,[tf.saved_model.tag_constants.SERVING], "/Users/ben/Dropbox/GoogleCloud/Detection/SavedModel/ssd_inception_v2_coco/saved_model/")  
        
label_map = label_map_util.load_labelmap("label.pbtxt")
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)
        
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    npdata=np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)   
    return npdata

# Definite input and output Tensors for sess.graph
image_tensor = sess.graph.get_tensor_by_name('image_tensor:0')

# Each box represents a part of the image where a particular object was detected.
detection_boxes = sess.graph.get_tensor_by_name('detection_boxes:0')

# Each score represent how level of confidence for each of the objects.
# Score is shown on the result image, together with the class label.
detection_scores = sess.graph.get_tensor_by_name('detection_scores:0')
detection_classes = sess.graph.get_tensor_by_name('detection_classes:0')
num_detections = sess.graph.get_tensor_by_name('num_detections:0')
for image_path in TEST_IMAGE_PATHS:
    
    image = Image.open(image_path)
    
    #basewidth = 300
    #wpercent = (basewidth/float(image.size[0]))
    #hsize = int((float(image.size[1])*float(wpercent)))
    #image = image.resize((basewidth,hsize), Image.ANTIALIAS)
    
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = load_image_into_numpy_array(image)
    
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    before = datetime.datetime.now()    
    (boxes, scores, classes, num) = sess.run([detection_boxes, detection_scores, detection_classes, num_detections],feed_dict={image_tensor: image_np_expanded})
    print("Prediction took : " + str(datetime.datetime.now() - before))  
    
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(image_np, np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores), category_index, use_normalized_coordinates=True,line_thickness=8)
    plt.figure(figsize=IMAGE_SIZE)
    fn=os.path.basename(image_path)
    plt.imsave("/Users/Ben/Dropbox/GoogleCloud/Detection/validation/" + fn,image_np)
    #plt.imshow(image_np)
            