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

### Path and model variables

ROOT = './'
PATH = ROOT + "./machine-learning/"
TRAIN_PATH = PATH + "train"
TEST_PATH = PATH + "test"
IMG_SIZE = 32
CHANNELS = 1
LABEL_FILE = "labels.txt"

### Get the labels from file
labels = []
with open(PATH + LABEL_FILE, "r") as file:
    labels = file.read().splitlines()

num_classes = len(labels)
print('Labels: ' + str(labels))
print('Number of classes: ' + str(num_classes))

### Extract the images from the folder, load them into an array, convert them to gray if necessary and attach its labels
i = 0
dataset = []
input_shape = (IMG_SIZE, IMG_SIZE, CHANNELS)
for folder in labels:
    counter = 0
    files = os.listdir(f'{ROOT}/images/{labels[i]}')
    for file in files:
        ext = file.split('.')[-1]
        if ext in ['jpg', 'png']:
            img = cv.imread(f'{ROOT}/images/{labels[i]}/{file}')
            if CHANNELS == 1:
                img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            img = cv.resize(img, input_shape[:2])
            dataset.append([img, i])
            counter += 1
    print(f'Add {counter} images with label {labels[i]} ')
    i += 1


X = []
y = []

for images, labels in dataset:
    X.append(images)
    y.append(labels)

print(f'Total images: {len(dataset)}')


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

# Create the CNN
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

# Compile and Train
model.compile(loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
)

batch_size = 4
epochs = 10
callbacks = [EarlyStopping(patience=2), board]

model.fit(X_train, y_cat_train, batch_size=batch_size, epochs=epochs, callbacks=callbacks, validation_split=0.1, )

# Model evaluation
loss, acc = model.evaluate(X_test, y_cat_test)

print("LOSS: {}, ACC: {}".format(loss, acc * 100))

pred = np.argmax(model.predict(X_test), axis=-1)
print(classification_report(y_test, pred))


# Model write to file
now = datetime.now()
str_date = now.strftime("%Y-%m-%d_%H%M%S")
file_name = f"models/stickers_{IMG_SIZE}x{IMG_SIZE}.h5"

model.save(file_name)

print("TRAINING PROCESS DONE!\n")

