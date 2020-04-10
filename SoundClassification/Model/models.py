
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, Flatten
from keras.layers import BatchNormalization
from keras.layers import Activation



def base_model(num_rows, num_columns, num_channels, num_labels):

    model = Sequential()
    model.add(Conv2D(filters=16, kernel_size=2, input_shape=(num_rows, num_columns, num_channels), activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=32, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=64, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(Conv2D(filters=128, kernel_size=2, activation='relu'))
    model.add(MaxPooling2D(pool_size=2))
    model.add(Dropout(0.2))

    model.add(GlobalAveragePooling2D())

    model.add(Dense(num_labels, activation='softmax'))

    return model


def batch_norm_model(num_rows, num_columns, num_channels, num_labels):
    model = Sequential()

    model.add(Conv2D(32, kernel_size=(2, 2), input_shape=(num_rows, num_columns, num_channels)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))

    model.add(Conv2D(48, kernel_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))

    model.add(Conv2D(120, kernel_size=(2, 2)))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())

    model.add(Dense(128))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(Dropout(0.25))

    model.add(Dense(64))
    model.add(BatchNormalization())
    model.add(Activation('relu'))
    model.add(Dropout(0.4))

    model.add(Dense(num_labels, activation='softmax'))

    return model
