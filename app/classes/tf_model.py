from tensorflow import keras
import yaml
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf
import cv2 as cv
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
from datetime import datetime

np.set_printoptions(suppress=True)
tf.compat.v1.disable_eager_execution()


class TFModel:

    def __init__(self, config_file='config.yml', model_name='sticker') -> None:
        with open(config_file) as file:
            config = yaml.safe_load(file)['model'][model_name]
        self.size = config['size']
        self.channels = config['channels']
        self.graph = load_model(config['file'])
        self.labels = config['default_labels']

    def predict(self, image: np.ndarray):
        if self.graph == 'keras.h5':
            return self.predict_keras(image)
        else:
            processed_image = self.__preprocess(image)
            prediction = self.graph.predict(processed_image)
            index = int(prediction.argmax(axis=1)[0])
            label = self.labels[index]
            return (index, label)

    def __preprocess(self, image: np.ndarray) -> np.ndarray:
        if self.channels == 1:
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        processed_image = cv.resize(image, (self.size, self.size), cv.INTER_AREA)
        processed_image = processed_image / 255
        processed_image = processed_image.reshape(1, self.size, self.size, self.channels)
        return processed_image

    def predict_keras(self, image: np.ndarray):
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array
        prediction = self.model.predict(data)
        index = int(prediction.argmax(axis=1)[0])
        label = self.labels[index]
        return (index, label)

