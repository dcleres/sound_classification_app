import os

import models
import model_cfg

from keras.callbacks import ModelCheckpoint
from datetime import datetime


class BaseModel:
    """
    This class defines the base_model and its basic functionalities.
    # TODO: Produce a confusion matrix plot of the data
    """
    def __init__(self, num_rows, num_columns, num_channels, num_labels, num_batch_size=256, num_epochs=50):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.num_channels = num_channels
        self.num_labels = num_labels
        self.num_batch_size = num_batch_size
        self.num_epochs = num_epochs

    def define_model(self, model="base"):
        # Construct model
        if model == "base":
            self.model = models.base_model(self.num_rows, self.num_columns, self.num_channels, self.num_labels)
            self.define_loss_and_optimizer(loss="categorical_crossentropy", metrics=["accuracy"], optimizer="adam")
        elif model == "batch_norm":
            self.model = models.batch_norm_model(self.num_rows, self.num_columns, self.num_channels, self.num_labels)
            self.define_loss_and_optimizer(loss="categorical_crossentropy", metrics=["accuracy"], optimizer="adadelta")
        else:
            assert model in ["base", "batch_norm"], "ERROR: Unknown model " + model

    def define_loss_and_optimizer(self, loss="categorical_crossentropy", metrics=["accuracy"], optimizer="adam"):
        # Compile the model
        self.model.compile(loss=loss, metrics=metrics, optimizer=optimizer)
        # Display model architecture summary
        self.model.summary()

    def train_model(self, x_train, y_train, x_val, y_val):
        """
        Train the model with a checkpoint that saves the model at each step.

        Arguments:
            x_train {np.array} -- Training data. Shape: (N, 256, 256, 1)
            y_train {np.array} -- Training labels. Shape: (N, 3)
            x_val {np.array} -- Validation data. Shape: (N, 256, 256, 1)
            y_val {np.array} -- Validation data. Shape: (N, 256, 256, 1)
        """
        saved_model_filename = os.path.join(model_cfg.MODEL_PATH, "saved_model_weights/weights_best_basic_cnn.hdf5")
        checkpointer = ModelCheckpoint(filepath=saved_model_filename, verbose=1, save_best_only=True)

        start = datetime.now()
        self.model.fit(
            x_train,
            y_train,
            batch_size=self.num_batch_size,
            epochs=self.num_epochs,
            validation_data=(x_val, y_val),
            callbacks=[checkpointer],
            verbose=1,
        )
        duration = datetime.now() - start
        print("Training completed in time: ", duration)

    def eval_model(self, x_train, y_train, x_test, y_test):
        # Evaluating the model on the training and testing set
        score = self.model.evaluate(x_train, y_train, verbose=0)
        print("Training Accuracy: ", score[1])

        score = self.model.evaluate(x_test, y_test, verbose=0)
        print("Testing Accuracy: ", score[1])
