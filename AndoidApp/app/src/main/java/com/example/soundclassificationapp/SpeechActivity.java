package com.example.soundclassificationapp;

    /*
     * Copyright 2017 The TensorFlow Authors. All Rights Reserved.
     *
     * Licensed under the Apache License, Version 2.0 (the "License");
     * you may not use this file except in compliance with the License.
     * You may obtain a copy of the License at
     *
     *       http://www.apache.org/licenses/LICENSE-2.0
     *
     * Unless required by applicable law or agreed to in writing, software
     * distributed under the License is distributed on an "AS IS" BASIS,
     * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     * See the License for the specific language governing permissions and
     * limitations under the License.
     */

/* The backbone of this app is based on the tutorial below, but I used a pretrained
   speech-to-text model instead.
   https://www.tensorflow.org/tutorials/audio_training
   The model files can be find in the 'assets' folder.
*/

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.graphics.drawable.AnimationDrawable;
import android.graphics.drawable.Drawable;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

import org.tensorflow.lite.DataType;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.common.FileUtil;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;
import org.tensorflow.lite.support.tensorbuffer.TensorBufferFloat;

import static android.media.AudioTrack.WRITE_BLOCKING;

/**
 * An activity that listens for audio from the built-in microphone for 5 seconds.
 * Then uses a pre-trained model to detect speech content. The trained model was trained on the
 * mel coefficient coming from an MFCC. Therefore, before the inference, the microphone output is
 * put through the MFCC function.
 * The output from this pre-processing step is fed to the loaded model and the inference is done.
 *
 * The app records a 5 seconds sample and the data between second 2 and 4 is used to do the
 * inference.
 */
public class SpeechActivity extends Activity {

    // Constants that control the behavior of the recognition code and model
    // settings.
    private static final int SAMPLE_RATE = 48000;
    private static final int SAMPLE_DURATION_MS = 5000; // The recorded samples is 5 seconds long.
    private static final int INFERENCE_DURATION_MS = 2000; // inference is done on a 2 second strip.
    private static final int RECORDING_LENGTH = (int) (SAMPLE_RATE * SAMPLE_DURATION_MS / 1000);
    private static final int INFERENCE_LENGTH = (int) (SAMPLE_RATE * INFERENCE_DURATION_MS / 1000);

    public static final String probability = "probability";
    public static final String classLabel = "label";
    public static final String recording = "recording";

    /** Labels corresponding to the output of the vision model. */
    private List<String> labels;

    // UI elements.
    private static final int REQUEST_RECORD_AUDIO = 13;
    private Button startButton;
    private static final String LOG_TAG = SpeechActivity.class.getSimpleName();

    // Working variables.
    short[] recordingBuffer = new short[RECORDING_LENGTH];
    int recordingOffset = 0;
    boolean shouldContinue = true;
    private Thread recordingThread;
    boolean shouldContinueRecognition = true;
    private Thread recognitionThread;
    private ReentrantLock recordingBufferLock = new ReentrantLock();
    private Interpreter tfLite;
    private AnimationDrawable recordingAnimation;
    private ImageView recordingImage;


    private void reset_all_attributes() {
        recordingBuffer = new short[RECORDING_LENGTH];
        recordingOffset = 0;
        shouldContinue = true;
        shouldContinueRecognition = true;
        recordingBufferLock = new ReentrantLock();
        recognitionThread = null;
        recordingThread = null;
        startButton.setText(" Start Recording");
        startButton.setCompoundDrawablesWithIntrinsicBounds(R.mipmap.speech_icon_round, 0, 0, 0);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Set up the UI.
        super.onCreate(savedInstanceState);
        setContentView(R.layout.speech_activity);

        recordingImage = (ImageView) findViewById(R.id.recording_image);
        recordingImage.setBackgroundResource(R.drawable.wave);
        recordingAnimation = (AnimationDrawable) recordingImage.getBackground();
        recordingImage.setVisibility(View.INVISIBLE);

        startButton = (Button) findViewById(R.id.micButton);
        startButton.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        reset_all_attributes();
                        startRecording();
                        startButton.setText(" Recording ...");
                        final Drawable drawableTop = getResources().getDrawable(R.mipmap.speech_icon_round);
                        startButton.setCompoundDrawablesWithIntrinsicBounds(null, drawableTop, null, null);
                        recordingImage.setVisibility(View.VISIBLE);
                        recordingAnimation.start();
                        Log.v(LOG_TAG, "Button Clicked");
                        //outputText.setText("");
                    }
                });

        //outputText = (TextView) findViewById(R.id.output_text);
        requestMicrophonePermission();
    }

    /** Memory-map the model file in Assets. */
    private static MappedByteBuffer loadModelFile(AssetManager assets, String modelFilename)
            throws IOException {
        AssetFileDescriptor fileDescriptor = assets.openFd(modelFilename);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    /** Asks for the authorization to use the microphone */
    private void requestMicrophonePermission() {
        requestPermissions(
                new String[] {android.Manifest.permission.RECORD_AUDIO}, REQUEST_RECORD_AUDIO);
    }

    @Override
    public void onRequestPermissionsResult(
            int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == REQUEST_RECORD_AUDIO
                && grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        }
    }

    public synchronized void startRecording() {
        if (recordingThread != null) {
            return;
        }
        Log.v(LOG_TAG, "Starting Recording");
        shouldContinue = true;
        recordingThread =
                new Thread(
                        new Runnable() {
                            @Override
                            public void run() {
                                record();
                            }
                        });
        recordingThread.start();
    }

    private void record() {
        android.os.Process.setThreadPriority(android.os.Process.THREAD_PRIORITY_AUDIO);

        // Estimate the buffer size we'll need for this device.
        int bufferSize =
                AudioRecord.getMinBufferSize(
                        SAMPLE_RATE, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);
        if (bufferSize == AudioRecord.ERROR || bufferSize == AudioRecord.ERROR_BAD_VALUE) {
            bufferSize = SAMPLE_RATE * 2;
        }
        short[] audioBuffer = new short[bufferSize / 2];

        AudioRecord record =
                new AudioRecord(
                        MediaRecorder.AudioSource.DEFAULT,
                        SAMPLE_RATE,
                        AudioFormat.CHANNEL_IN_MONO,
                        AudioFormat.ENCODING_PCM_16BIT,
                        bufferSize);

        if (record.getState() != AudioRecord.STATE_INITIALIZED) {
            Log.e(LOG_TAG, "Audio Record can't initialize!");
            return;
        }

        record.startRecording();
        Log.v(LOG_TAG, "Start recording");

        while (shouldContinue) {
            int numberRead = record.read(audioBuffer, 0, audioBuffer.length);
            Log.v(LOG_TAG, "read: " + numberRead);
            int maxLength = recordingBuffer.length;
            recordingBufferLock.lock();
            try {
                if (recordingOffset + numberRead < maxLength) {
                    System.arraycopy(audioBuffer, 0, recordingBuffer, recordingOffset, numberRead);
                } else {
                    shouldContinue = false;
                }
                recordingOffset += numberRead;
            } finally {
                recordingBufferLock.unlock();
            }
        }
        record.stop();
        record.release();
        recordingImage.setVisibility(View.INVISIBLE);
        startRecognition();
    }

    public synchronized void startRecognition() {
        if (recognitionThread != null) {
            return;
        }
        shouldContinueRecognition = true;
        recognitionThread =
                new Thread(
                        new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    recognize();
                                } catch (IOException e) {
                                    e.printStackTrace();
                                }
                            }
                        });
        recognitionThread.start();
    }

    private void recognize() throws IOException {
        Log.v(LOG_TAG, "Start recognition");
        short[] inputBuffer = new short[RECORDING_LENGTH];
        double[] doubleInputBuffer = new double[INFERENCE_LENGTH];
        float[] floatInputBuffer = new float[INFERENCE_LENGTH];

        // This makes it possible to modify the UI inside this thread.
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Stuff that updates the UI
                startButton.setText("Inference Started ...");
            }
        });

        recordingBufferLock.lock();
        try {
            int maxLength = recordingBuffer.length;
            System.arraycopy(recordingBuffer, 0, inputBuffer, 0, maxLength);
        } finally {
            recordingBufferLock.unlock();
        }

        // We need to feed in float values between -1.0 and 1.0, so divide the
        // signed 16-bit inputs.
        int time_offset_seconds = 2;
        int offset_idx = time_offset_seconds * 48000;
        for (int i = 0; i < INFERENCE_LENGTH; ++i) {
            doubleInputBuffer[i] = inputBuffer[i + offset_idx] / 32767.0;
            floatInputBuffer[i] = inputBuffer[i + offset_idx] / 32767.0f;
        }

        //MFCC java library.
        MFCC mfccConvert = new MFCC();
        float[] mfccInput = mfccConvert.process(doubleInputBuffer);
        float[] mfcc_input_padded = create_padded_float_array(mfccInput);

        // Load the tflite model with pre-trained weights
        try{
            MappedByteBuffer tfliteModel = loadModelFile(getAssets(), "speech_class_model.tflite");
            tfLite = new Interpreter(tfliteModel);
            Log.v(LOG_TAG, "Model Loaded");
        } catch (IOException e){
            Log.e("tfliteSupport", "Error reading model", e);
        }

        // Reads type and shape of input and output tensors, respectively.
        int imageTensorIndex = 0;
        int[] imageShape = tfLite.getInputTensor(imageTensorIndex).shape(); // {1, height, width, 1}
        DataType imageDataType = tfLite.getInputTensor(imageTensorIndex).dataType();
        int probabilityTensorIndex = 0;
        int[] probabilityShape =
                tfLite.getOutputTensor(probabilityTensorIndex).shape(); // {1, NUM_CLASSES}
        DataType probabilityDataType = tfLite.getOutputTensor(probabilityTensorIndex).dataType();

        // Creates the input tensor.
        TensorBuffer inputTensor = TensorBufferFloat.createFixedSize(imageShape, imageDataType);
        inputTensor.loadArray(mfcc_input_padded);

        // Creates the output tensor and its processor.
        TensorBuffer outputProbabilityBuffer = TensorBuffer.createFixedSize(probabilityShape, probabilityDataType);

        // tfLite runs the inference we the trained model
        tfLite.run(inputTensor.getBuffer(), outputProbabilityBuffer.getBuffer().rewind());

        // Gets the results from the inference
        Log.v(LOG_TAG, "Output Probabilities" + Arrays.toString(outputProbabilityBuffer.getFloatArray()));
        float[] my_result_array = outputProbabilityBuffer.getFloatArray();

        // Cleaning Up Things
        tfLite.close();
        tfLite = null;

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Stuff that updates the UI
                startButton.setText("Inference Done.");
            }
        });

        Log.v(LOG_TAG, "End recognition");

        double max_probability = getLargestFloat(my_result_array);
        int label_index = getIndexOfLargest(my_result_array);
        labels = FileUtil.loadLabels( this , "labels.txt" );
        String label = labels.get(label_index);
        double probability_value = max_probability;

        Log.v(LOG_TAG, "Class Label = " + label);
        Log.v(LOG_TAG, "Probability = " + probability_value);

        // Call the new activity and pass along some information via putExtras
        Intent intent = new Intent(this, InferenceResultActivity.class);
        intent.putExtra(probability, probability_value);
        intent.putExtra(classLabel, label);
        intent.putExtra(recording, floatInputBuffer);
        startActivity(intent);

    }

    private float[] create_padded_float_array(float[] mfcc_transform) {
        float[] mfcc_input_padded = new float[256*256];

        for (int i = 0;  i < mfcc_transform.length ; i++) {
            int column_mfcc = i / 20;
            int idx_mfcc = i % 20;
            mfcc_input_padded[256 * idx_mfcc + column_mfcc] = mfcc_transform[20 * column_mfcc + idx_mfcc];
        }
        return mfcc_input_padded;
    }

    public int getIndexOfLargest( float[] array )
    {
        if ( array == null || array.length == 0 ) return -1; // null or empty
        int largest = 1;
        for ( int i = 0; i < array.length; i++ )
        {
            if ( array[i] > array[largest] ) largest = i;
        }
        return largest; // position of the first largest found
    }

    public float getLargestFloat( float[] array )
    {
        if ( array == null || array.length == 0 ) return -1; // null or empty

        float largest = array[0];
        for ( int i = 1; i < array.length; i++ )
        {
            if ( array[i] > largest ) {
                largest = array[i];
            }
        }
        return largest; // position of the first largest found
    }
}

