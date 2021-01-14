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
from tensorflow.keras.preprocessing.image import ImageDataGenerator

### Path and model variables

ROOT = '.'
PATH = ROOT + "/machine-learning/"
TRAIN_PATH = PATH + "train"
TEST_PATH = PATH + "test"
IMG_SIZE = 100
CHANNELS = 1
MODEL = 'drain'
LABEL_FILE = MODEL + "_labels.txt"

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
    files = os.listdir(f'./images/{MODEL}/{labels[i]}')
    for file in files:
        ext = file.split('.')[-1]
        if ext in ['jpg', 'png']:
            img = cv.imread(f'./images/{MODEL}/{labels[i]}/{file}')
            if CHANNELS == 1:
                img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            img = cv.resize(img, input_shape[:2])
            dataset.append([img, i])
            counter += 1
    print(f'Add {counter} images with label {labels[i]} ')
    i += 1


X = []
y = []

for image, label in dataset:
    X.append(image)
    y.append(label)

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

datagen = ImageDataGenerator(
    rotation_range=10,
    height_shift_range=0.1,
    width_shift_range=0.1
)

datagen.fit(X_train)

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

batch_size = 8
epochs = 30
callbacks = [EarlyStopping(patience=2), board]
# callbacks = []

# model.fit(datagen.flow(X_train, y_cat_train, batch_size=16),
#     steps_per_epoch=(len(X_train) // batch_size),
#     validation_data=(X_test, y_cat_test),
#     epochs=epochs)

model.fit(X_train, y_cat_train, batch_size=batch_size, epochs=epochs, callbacks=callbacks, validation_split=0.1, )

# Model evaluation
loss, acc = model.evaluate(X_test, y_cat_test)

print("LOSS: {}, ACC: {}".format(loss, acc * 100))

pred = np.argmax(model.predict(X_test), axis=-1)
print(classification_report(y_test, pred))


# Model write to file
now = datetime.now()
str_date = now.strftime("%Y-%m-%d_%H%M%S")
# file_name = f"keras_models/{MODEL}_{IMG_SIZE}x{IMG_SIZE}.h5"
file_name = f"drain_graph.h5"

model.save(file_name)

print("TRAINING PROCESS DONE!\n")

