# region imports
import os
import random
import cv2 as cv
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

## New version of Keras (Tensorflow)
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense, Flatten, Conv2D, MaxPool2D, Dropout
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard

# endregion

ROOT = './'
PATH = ROOT + "./machine-learning/"
TRAIN_PATH = PATH + "train"
TEST_PATH = PATH + "test"
IMG_SIZE = 32
CHANNELS = 1

input_shape = (IMG_SIZE, IMG_SIZE, CHANNELS)

labels = []

with open(PATH + "labels.txt", "r") as file:
    labels = file.read().splitlines()

num_classes = len(labels)
i = 0
dataset = []

print('labels: ', labels)
print(ROOT)

for folder in labels:
    files = os.listdir(f'{ROOT}/images/{labels[i]}')
    for file in files:
        ext = file.split('.')[-1]
        if ext in ['jpg', 'png']:
            img = cv.imread(f'{ROOT}/images/{labels[i]}/{file}', 0)
            img = cv.resize(img, input_shape[:2])
            dataset.append([img, i])
    i += 1

X = []
y = []

for images, labels in dataset:
    X.append(images)
    y.append(labels)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, CHANNELS)
X = X / 255


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
)

x_train_mean = np.mean(X_train, axis=0)
X_train -= x_train_mean
X_test -= x_train_mean

y_cat_train = to_categorical(y_train, num_classes)
y_cat_test = to_categorical(y_test, num_classes)

model = Sequential()

model.add(
    Conv2D(filters=32, kernel_size=(3,3), input_shape=input_shape, activation="relu")
)
model.add(MaxPool2D(pool_size=(2, 2)))

model.add(Conv2D(filters=64, kernel_size=(3,3), activation="relu"))
model.add(MaxPool2D(pool_size=(2, 2)))

model.add(Flatten())

model.add(Dense(128, activation="relu"))
model.add(Dropout(0.2))
model.add(Dense(num_classes, activation="softmax", kernel_initializer='he_normal'))


log_dir = 'logs\\fit'

board = TensorBoard(
    log_dir=log_dir,
    histogram_freq=1,
    write_graph=True,
    write_images=True,
    update_freq='epoch',
    profile_batch=2,
    embeddings_freq=1
)

model.compile(loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
)

model.fit(X_train, y_cat_train, batch_size=4, epochs=10, validation_split=0.1, callbacks=[EarlyStopping(patience=2), board])

loss, acc = model.evaluate(X_test, y_cat_test)

print("LOSS: {}, ACC: {}".format(loss, acc * 100))

pred = np.argmax(model.predict(X_test), axis=-1)
print(classification_report(y_test, pred))


# with timestamp, acc and loss
now = datetime.now()
str_date = now.strftime("%Y-%m-%d_%H%M%S")
file_name = f"models/stamps_{str_date}.h5"

# model.save(file_name)
# model.save('stamps_keras.h5')
model.save('tankstickers.h5')

print("DONE!\n")





