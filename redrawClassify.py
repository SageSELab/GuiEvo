from config import *
import os
import sys
import numpy as np
import tensorflow as tf
from google.protobuf import text_format
from tensorflow.python.framework import graph_io
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file
from tensorflow.python.platform import gfile



"""
def printTensors(pb_file):
    # read pb into graph_def
    with gfile.FastGFile(pb_file,'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    # import graph_def
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    # print operations
    for op in graph.get_operations():
        print(op.values())
"""



def read_tensor_from_image_file(file_name, input_height=299, input_width=299, input_mean=0, input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.io.read_file(file_name, input_name)
    image_reader = tf.image.decode_png(file_reader, channels=3, name="png_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.compat.v1.Session()
    result = sess.run(normalized)
    return result


    

def predict_label(component):
    np.set_printoptions(suppress=True)
    tf.compat.v1.reset_default_graph()
    #printTensors(Modelcheckpoint)
    labels = []
    output = []
    proto_as_ascii_lines = tf.io.gfile.GFile(label_filepath).readlines()
    for l in proto_as_ascii_lines:
        labels.append(l.rstrip())
    with tf.compat.v1.Session(graph = tf.Graph()) as sess:
        with gfile.GFile(Modelcheckpoint,'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
            sess.graph.as_default()
            tf.import_graph_def(graph_def,name='')
            image_data = read_tensor_from_image_file(component)
            softmax_tensor = sess.graph.get_tensor_by_name('InceptionV3/Predictions/Reshape_1:0')
            predictions = sess.run(softmax_tensor,{'input:0': image_data})
            topprediction = predictions[0].argsort()[-len(predictions[0]):][::-1]
            predicted_label = labels[topprediction[0]]
            return predicted_label


