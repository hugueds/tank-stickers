import tensorflow as tf
import cv2 as cv
from tensorflow.keras.models import load_model
tf.compat.v1.disable_eager_execution()

class Model:

    def __init__(self, config=None):        
        self.size = int(config['SIZE'])
        self.channels = int(config['CHANNELS'])
        self.labels = config['LABELS'].split(',')        
        file = config['FILE']
        self.graph = load_model(file)

    def predict(self, image):
        processed_image = self.preprocess(image)
        prediction = self.graph.predict(processed_image)
        index = int(prediction.argmax(axis=1)[0])
        label = self.labels[index]        
        return (index, label)

    def preprocess(self, image):
        if self.channels == 1:
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
                    
        processed_image = cv.resize(image, (self.size, self.size), cv.INTER_AREA)
        processed_image = processed_image / 255
        processed_image = processed_image.reshape(1, self.size, self.size, self.channels)
        return processed_image
