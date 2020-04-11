import BaseModel

if __name__ == "__main__":

    num_rows = 256
    num_columns = 256
    num_channels = 1
    num_labels = 3
    num_batch_size = 16
    num_epochs = 100
    model_name = "base"
    is_exporting_to_tf_lite = True

    base_model = BaseModel.BaseModel(
        num_rows, num_columns, num_channels, num_labels, num_batch_size=num_batch_size, num_epochs=num_epochs
    )

    if is_exporting_to_tf_lite:
        base_model.export_model_to_tf_lite()
    else:
        base_model.export_model(model_name=model_name)
