import BaseModel
from SoundClassification.DataProcessing import load_data


if __name__ == '__main__':

    random_seed = 1
    test_size = 0.2
    num_rows = 256
    num_columns = 256
    num_channels = 1
    num_labels = 3
    num_batch_size = 8
    num_epochs = 10

    X_train, X_test, y_train, y_test = load_data.get_train_test_data(test_size=test_size, random_state=random_seed)

    base_model = BaseModel.BaseModel(num_rows, num_columns, num_channels, num_labels, num_batch_size=num_batch_size, num_epochs=num_epochs)
    base_model.define_model(model="batch_norm")
    base_model.define_loss_and_optimizer()
    base_model.train_model(X_train, y_train, X_test, y_test)
