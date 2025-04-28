import os

import numpy as np
import tensorflow as tf
from PIL import Image
from matplotlib import pyplot as plt
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model

from app.core.config import Config

img_height, img_width = 128, 128
batch_size = 32

class ModelCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if logs.get('val_loss') < 0.1 and logs.get('val_accuracy') > 0.9:
      self.model.stop_training = True


# def create_categorical_model(input_shape, num_classes=3):
#     model = tf.keras.models.Sequential([
#         Input(shape=input_shape),
#         Conv2D(32, (3, 3), activation='relu'),
#         MaxPooling2D((2, 2)),
#         Flatten(),
#         Dense(128, activation='relu'),
#         Dense(num_classes, activation='softmax')
#     ])
#     model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
#     return model


def create_binary_model():
    model = tf.keras.models.Sequential([
        # Input(shape=(img_height, img_width, 1)),    # 1 channel in grayscale
        # Conv2D(32, (3, 3), activation='relu'),
        # MaxPooling2D((2, 2)),
        Conv2D(16, (3,3), activation='relu', input_shape=(img_height, img_width, 1)),
        MaxPooling2D(2, 2),
        Conv2D(32, (3,3), activation='relu'),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(1, activation='sigmoid')  # Sigmoid for binary classification
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# def create_vgg16_model(input_shape):
#     base_model = VGG16(weights='imagenet', include_top=False, input_shape=(img_height, img_width, 3))
#     for layer in base_model.layers:
#         layer.trainable = False
#     x = Flatten()(base_model.output)
#     x = Dense(128, activation='relu')(x)
#     x = Dense(1, activation='sigmoid')(x)
#
#     model = Model(inputs=base_model.input, outputs=x)
#     model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#     return model

def create_model():
    print('Creating model...')
    model = create_binary_model()
    # model = create_vgg16_model(input_shape)
    return model


def train_model(model, train_data, validation_data, epochs=20):
    print('Training model...')
    callbacks = ModelCallback()
    history = model.fit(
        train_data,
        epochs=epochs,
        validation_data=validation_data,
        callbacks=[callbacks]
    )
    return history

def plot_history(history):
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

def save_model(model, path):
    print('Saving model...')
    model.save(path)


def load_model(path):
    model = tf.keras.models.load_model(path)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model


# def predict_categorical_image_class(model_path, image):
#     model = load_model(model_path)
#     predictions = model.predict(image)
#     return predictions.argmax()


def predict_binary_image_class(image_path, model_path=None, model=None, threshold=0.5, ):
    if not model_path and not model:
        raise ValueError('Either model_path or model is required.')

    if not model and model_path:
        model = load_model(model_path)

    img_array = preprocess_image(image_path)
    prediction = model.predict(img_array)
    prediction_class = "real_estate" if int(prediction > threshold) else "invalid"
    return prediction, prediction_class


def predict_image_class(model_path, image_path, threshold=0.5):
    return predict_binary_image_class(model_path, image_path, threshold)


def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.convert('L')  # grayscale
    img = img.resize((img_height, img_width))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = img_array.reshape((1, img_height, img_width, 1))
    # if img_array.shape[-1] == 3:  # 3 channels for RGB
    #     img_array = img_array.reshape((1, img_height, img_width, 3))
    # else:
    #     img_array = img_array.reshape((1, img_height, img_width, 1))
    return img_array


def train_and_save(dataset_path, saved_model_path, plot_training_history=False):
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='binary',
        color_mode='grayscale',
        subset='training',
        shuffle=True
    )

    val_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(img_height, img_width),
        batch_size=batch_size,
        class_mode='binary',
        color_mode='grayscale',
        subset='validation',
        shuffle=False
    )

    model = create_model()

    history = train_model(
        model,
        train_generator,
        val_generator,
        epochs=15
    )

    if plot_training_history:
        plot_history(history)

    save_model(model, saved_model_path)


def main():
    config = Config()
    classifier_path = os.path.join(config.static_path, "classifier")
    dataset_path = os.path.join(classifier_path, "dataset")
    saved_model_path = os.path.join(classifier_path, "classifier_weights.h5")
    train_and_save(dataset_path, saved_model_path)


if __name__ == '__main__':
    main()
