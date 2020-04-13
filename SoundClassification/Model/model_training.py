import BaseModel
from SoundClassification.DataProcessing import load_data


if __name__ == "__main__":

    random_seed = 1
    test_size = 0.1
    num_channels = 1
    num_labels = 3
    num_batch_size = 16
    num_epochs = 100
    # model_name = "batch_norm"
    model_name = "larger_base_model"
    # model_name = "base"
    # model_name = "lambda_base"
    max_samples = 2500
    is_exporting_to_tf_lite = True
    is_using_mfcc = True

    if is_using_mfcc:
        num_rows = 256
        num_columns = 256
    else:
        num_rows = 1
        num_columns = 96000

    X_train, X_test, y_train, y_test = load_data.get_train_test_data(
        test_size=test_size, random_state=random_seed, max_samples=max_samples, is_using_mfcc=is_using_mfcc
    )

    base_model = BaseModel.BaseModel(
        num_rows, num_columns, num_channels, num_labels, num_batch_size=num_batch_size, num_epochs=num_epochs
    )
    base_model.define_model(model=model_name)
    base_model.define_loss_and_optimizer()
    base_model.train_model(X_train, y_train, X_test, y_test)

    if is_exporting_to_tf_lite:
        base_model.export_model_to_tf_lite()
    else:
        base_model.export_model(model_name=model_name)
