# Sound Classification Application for Android Phones

This project was done for the Center for Digital Health Interventions 
in the frame of the Challenge for technical applicants.

=============================================================================

## Aim of the coding challenge
Take no more than 2-3 days to write a small android application which classifies singing vs speaking vs silence of the last 2 seconds based on microphone sensor data. Your solution should utilise at least one machine learning approach. You are welcome to make use of third party libraries as long as they are not pre-trained on the specific task at hand. The classification results should be displayed on the screen.

## Deliverable

In case you accept this challenge, provide us with a small set of slides describing your approach, the commented source code and a compiled .apk supporting Android 6.0+.

## Used dataset
The dataset used for training the models was the [AudioSet](https://research.google.com/audioset/) dataset from Google. This dataset is one of the largest sound datasets available worldwide and presents recording from YouTube that are 10 seconds long and were labeled by human beings.
The folder called `Data`is focused on extracting the data from this dataset and to copy them locally. The data from this dataset is sampled at 48 000 Hz. Information regarding the download of this data is available [here](https://research.google.com/audioset/download.html).

## Model
The model was trained on 2 seconds recordings. In order to get the 2 seconds recording for the 10 seconds YouTube. It was decided to split the 10 seconds YouTube data in 2 seconds strips. The first and last strip were discarded to ensure the quality of the data. Therefore, one video lead to 3 training samples.
The model was trained on a 90% training and 10% testing ratio and reached an accuracy above 96% on the training and validation sets. This is an impressive result since some of the training data might actually contain wrong labels because of the 2 seconds division of the training data.
The model was trained on 100 epochs and took 8 hours to run on a MacBook Pro 15" from 2016.

![Accuracy](https://github.com/dcleres/sound_classification_app/blob/master/SoundClassification/Model/saved_models/training_validation_accuracy.png)

![Loss](https://github.com/dcleres/sound_classification_app/blob/master/SoundClassification/Model/saved_models/training_validation_loss_values.png)

## Android Application
The trained weights on the deep neural network was saved to a tflife file which could then be read on a mobile device.
The user of the app could sing, speak, or say nothing to the app and get a prediction of whether the user sang, spoke or said nothing
to the camera. The App is a 2 screen app and shows nice performance. Some screenshots can be found below.

![mainscreen](https://github.com/dcleres/sound_classification_app/blob/master/screenshots/main_screen.png)

![mainscreen](https://github.com/dcleres/sound_classification_app/blob/master/screenshots/recording.png)

![mainscreen](https://github.com/dcleres/sound_classification_app/blob/master/screenshots/inference_done_state.png)

![mainscreen](https://github.com/dcleres/sound_classification_app/blob/master/screenshots/inference_result.png)


## Acknowledgement
This App was implemented for the Center for Digital Health Interventions by David Cleres.
The dataset is made available by Google Inc. under a Creative Commons Attribution 4.0 International (CC BY 4.0) license, while the ontology is available under a Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) license.
