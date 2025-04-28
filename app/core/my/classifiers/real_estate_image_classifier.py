import logging
import os
import traceback
from enum import Enum

import numpy as np
import tensorflow as tf
from PIL import Image
from matplotlib import pyplot as plt
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from app.core.config import config
from app.core.my.extractors.pdf_image_extractor import ImageSize


class RealEstateImageClassifierClass(Enum):
    REAL_ESTATE = 'REAL_ESTATE'
    INVALID = 'INVALID'


class ModelCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if logs.get('val_loss') < 0.1 and logs.get('val_accuracy') > 0.9:
      self.model.stop_training = True


class RealEstateImageClassifier:
    def __init__(self):
        self.model = None
        self.img_height = ImageSize.HEIGHT.value
        self.img_width = ImageSize.WIDTH.value
        self.model_path = os.path.join(config.classifier_path, 'real_estate_images', 'model.keras')
        self.training_dataset_path = os.path.join(config.classifier_path, 'real_estate_images', 'training_dataset' )

    def set_image_size(self, img_height: int, img_width: int):
        self.img_height = img_height
        self.img_width = img_width

    def predict_image_class(self, image_path: str, threshold=0.5) -> RealEstateImageClassifierClass:
        model = self.load_model()
        img_array = self.preprocess_image(image_path)
        prediction = model.predict(img_array)
        return RealEstateImageClassifierClass.REAL_ESTATE if int(prediction > threshold) else RealEstateImageClassifierClass.INVALID

    def is_real_estate_image(self, image_path: str) -> bool:
        try:
            return self.predict_image_class(image_path) == RealEstateImageClassifierClass.REAL_ESTATE
        except Exception as e:
            logging.error(f'Error while predicting real estate image for file {image_path}: {e}')
            traceback_str = traceback.format_exc()
            logging.error(traceback_str)
            return False

    def preprocess_image(self, image_path):
        img = Image.open(image_path)
        img = img.convert('L')  # grayscale
        img = img.resize((self.img_height, self.img_width))
        img_array = np.array(img)
        img_array = img_array / 255.0 # normalizing [0, 1]
        img_array = img_array.reshape((1, self.img_height, self.img_width, 1)) # 1 channel for grayscale
        return img_array

    def load_model(self):
        if self.model is None:
            self.model = tf.keras.models.load_model(self.model_path)
            self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return self.model

    def create_model(self):
        model = tf.keras.models.Sequential([
            Conv2D(16, (3, 3), activation='relu', input_shape=(self.img_height, self.img_width, 1)), # 1 channel for grayscale
            MaxPooling2D(2, 2),
            Conv2D(32, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(1, activation='sigmoid')  # Sigmoid for binary classification
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def train_the_model(self, training_dataset_path=None, model_path=None, plot_training_history=False):
        if training_dataset_path is None:
            training_dataset_path = self.training_dataset_path

        train_datagen = ImageDataGenerator(
            rescale=1. / 255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )

        batch_size = 32

        train_generator = train_datagen.flow_from_directory(
            training_dataset_path,
            target_size=(self.img_height, self.img_width),
            batch_size=batch_size,
            class_mode='binary',
            color_mode='grayscale',
            subset='training',
            shuffle=True
        )

        val_generator = train_datagen.flow_from_directory(
            training_dataset_path,
            target_size=(self.img_height, self.img_width),
            batch_size=batch_size,
            class_mode='binary',
            color_mode='grayscale',
            subset='validation',
            shuffle=False
        )

        model = self.create_model()

        history = self.fit_model(
            model,
            train_generator,
            val_generator
        )

        if plot_training_history:
            self.plot_history(history)

        self.save_model(model, model_path)

    def fit_model(self, model, train_data_generator, validation_data_generator, epochs=20):
        print('Training model...')
        callbacks = ModelCallback()
        history = model.fit(
            train_data_generator,
            epochs=epochs,
            validation_data=validation_data_generator,
            callbacks=[callbacks]
        )
        return history

    def plot_history(self, history):
        acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']
        loss = history.history['loss']
        val_loss = history.history['val_loss']
        epochs = range(1, len(acc) + 1)

        plt.figure(figsize=(12, 6))

        plt.subplot(1, 2, 1)
        plt.plot(epochs, acc, 'b', label='Training accuracy')
        plt.plot(epochs, val_acc, 'r', label='Validation accuracy')
        plt.title('Training and validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(epochs, loss, 'b', label='Training loss')
        plt.plot(epochs, val_loss, 'r', label='Validation loss')
        plt.title('Training and validation loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def save_model(self, model, path=None):
        print('Saving model...')
        if path is None:
            path = self.model_path
        model.save(path)


