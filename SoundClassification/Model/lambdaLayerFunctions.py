import numpy as np 
import tensorflow as tf


def mfcc_layer(X):
    """
    This method is used as the first layer of the neural network. By doing so the network is able to do the
    mfcc transform on it own.

    Arguments:
        X {tf.Tensor} -- raw data from the wav file

    Returns:
        np.array -- Array that contains the mfcc transformed data
    """
    ## Convert the TensorFlow tensor to np.array
    X_np = tf.make_ndarray(tf.make_tensor_proto(X))
    print(X_np.shape)

    X = tf.convert_to_tensor(X_np)
    print(X.get_shape())
    return X


def mfcc_layer_output_shape(X):
    print(X)
    return (50, 256, 256, 1)


def some_function(X):
    return X.numpy()
