import yaml
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
import cv2 as cv
import numpy as np
from tensorflow.keras.models import load_model

tf.compat.v1.disable_eager_execution()


class TFModel:

    def __init__(self, config_file='config.yml', model_name='sticker'):
        with open(config_file) as file:
            config = yaml.safe_load(file)['model'][model_name]                

        self.size = config['size']
        self.channels = config['channels']
        self.graph = load_model(config['file'])
        self.labels = config['default_labels']

    def predict(self, image: np.ndarray):
        processed_image = self.preprocess(image)
        prediction = self.graph.predict(processed_image)
        index = int(prediction.argmax(axis=1)[0])
        label = self.labels[index]
        return (index, label)

    def preprocess(self, image: np.ndarray):
        if self.channels == 1:
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        processed_image = cv.resize(image, (self.size, self.size), cv.INTER_AREA)
        processed_image = processed_image / 255
        processed_image = processed_image.reshape(1, self.size, self.size, self.channels)
        return processed_image
