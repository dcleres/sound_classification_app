import numpy as np
import soundfile as sf
import librosa
from sklearn.preprocessing import LabelBinarizer
import os
from sklearn.model_selection import train_test_split
import model_cfg


def convert_data_to_mfcc(wave, sampling_rate, max_pad_len=256, padding=True):
    """
    This function converts the wave single which is of dimension (96000, 2) into
    a padded mfcc transform which can then be fed as picture tu the neural network.
    We pad until we have a square image of size 256x256 so that all convolution operations
    can be apply without running out of space. 256 was chosen since it is an exponent of 2
    therefore upscaling and maxpooling opetation can be done easily.

    Arguments:
        wave {np.array} -- wave signal extracted from the flac files.
        sampling_rate {int} -- sampling rate of the sample.

    Keyword Arguments:
        max_pad_len {int} -- Padding length (default: {256})
        padding {bool} -- Whether padding should be applied (default: {True})

    Returns:
        np.array -- 2d numpy array which is the mfcc transform.
    """
    mfcc = librosa.feature.mfcc(wave, sr=sampling_rate)
    pad_width = max_pad_len - mfcc.shape[1]
    pad_height = max_pad_len - mfcc.shape[0]
    return np.pad(mfcc, pad_width=((0, pad_height), (0, pad_width)), mode='constant')  # padding to have consistent mfcc size


def shorten_recording(data, samplerate):
    """
    The sample rate is in hertz. It was decided to keep only the 6 seconds in the middle of the audio recording.
    """
    duration = 2  # duration in seconds
    samples_per_n_seconds = samplerate * duration
    X_samples = np.array([]).reshape(-1, samples_per_n_seconds, 2)

    for t_start in range(9600, 38400, 9600):
        X_samples = np.concatenate((X_samples, data[t_start:t_start + samples_per_n_seconds].reshape(1, samples_per_n_seconds, 2)), axis = 0)

    return X_samples


def apply_mfcc(X, label, sampling_rate=48000):

    mfcc_X = []
    for audio_recording in X:
        mfcc_X.append(convert_data_to_mfcc(audio_recording[:,0], sampling_rate))
    labels = [label] * X.shape[0]

    return np.array(mfcc_X), np.array(labels)


def build_train_array(label, max_samples=200):

    X = np.array([]).reshape(-1, 96000, 2, 1)  # 96 000 is 2 seconds at sample rate 48 000
    X_mfcc = np.array([]).reshape(-1, 256, 256, 1)

    for filename in os.listdir(os.path.join(model_cfg.AUDIOSET_PATH, label)):
        data_path = os.path.join(model_cfg.AUDIOSET_PATH, label, filename)
        data, samplerate = sf.read(data_path)

        # Crop 2 seconds pieces of the audio to train on 2 second files
        X_samples = shorten_recording(data, samplerate)
        X = np.concatenate((X, X_samples.reshape(-1, 96000, 2, 1)), axis=0)

        for idx in range(len(X_samples)):
            X_mfcc_samples = convert_data_to_mfcc(np.asfortranarray(X_samples[idx, :, 0]), samplerate)
            X_mfcc = np.concatenate((X_mfcc, X_mfcc_samples.reshape(-1, 256, 256, 1)), axis=0)

        if X.shape[0] > max_samples:
            break

    labels = [label] * X.shape[0]
    labels_mfcc = [label] * X_mfcc.shape[0]

    return X, X_mfcc, labels, labels_mfcc


def get_all_sound_data(max_samples=100):
    X_speech, X_mfcc_speech, labels_speech, labels_mfcc_speech = build_train_array("speech", max_samples=max_samples)
    X_silence, X_mfcc_silence, labels_silence, labels_mfcc_silence = build_train_array("silence", max_samples=max_samples)
    X_singing, X_mfcc_singing, labels_singing, labels_mfcc_singing = build_train_array("singing", max_samples=max_samples)

    X = np.concatenate((X_speech, X_silence, X_singing), axis=0)
    X_mfcc = np.concatenate((X_mfcc_speech, X_mfcc_silence, X_mfcc_singing), axis=0)
    labels = labels_speech + labels_silence + labels_singing
    labels_mfcc = labels_mfcc_speech + labels_mfcc_silence + labels_mfcc_singing

    encoder = LabelBinarizer()
    categorical_label = encoder.fit_transform(labels)
    categorical_label_mfcc = encoder.fit_transform(labels_mfcc)

    return X, X_mfcc, categorical_label, categorical_label_mfcc


def get_train_test_data(test_size=0.2, random_state=1):
    X, X_mfcc, y_categorical, categorical_label_mfcc = get_all_sound_data()
    X_train, X_test, y_train, y_test = train_test_split(X_mfcc, categorical_label_mfcc, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test
