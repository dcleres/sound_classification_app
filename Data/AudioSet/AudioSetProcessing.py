#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "David Cleres"
__copyright__ = "Copyright 2020, Sound Classification App"
__credits__ = ["David Cleres"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "David Cleres"
__email__ = "davidcleres@gmail.com"
__status__ = "Development"


import pandas as pd


class AudioSetProcessing:
    """
    This class make it possible to work with the AudioSet Dataset from Google.
    """
    def __init__(self):
        self.data_csv_filename = "Data/AudioSet/unbalanced_train_segments.csv"
        self.data_csv = pd.read_csv(self.data_csv_filename)
        self.audio_labels_speech = ["Speech", "Male speech, man speaking", "Female speech, woman speaking", "Child speech, kid speaking", "Conversation", "Narration, monologue", "Speech synthesizer"]
        self.audio_labels_singing = ["Singing", "Choir", "Yodeling", "Chant", "Male singing", "Female singing", "Child singing", "Synthetic singing", "Rapping"]
        self.audio_labels_silence = ["Breathing", "Walk, footsteps", "Silence"]

        self.get_data_from_single_category()


    def get_data_from_single_category(self):
        """
        This function aims to extract the row which are only speech, only singing, and only silence.
        Data that has labels from several categories is discarded.
        """
        self.audio_data = 
        self.singing_data = 
        self.silence_data = 

        
