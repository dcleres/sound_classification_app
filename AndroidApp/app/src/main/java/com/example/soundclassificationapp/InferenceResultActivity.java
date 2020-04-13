package com.example.soundclassificationapp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import static android.media.AudioTrack.WRITE_BLOCKING;

public class InferenceResultActivity extends AppCompatActivity {

    private Button replayButton;
    private static final String LOG_TAG = InferenceResultActivity.class.getSimpleName();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_inference_result);


        // Get the Intent that started this activity and extract the string
        Intent intent = getIntent();
        double probability = intent.getDoubleExtra(SpeechActivity.probability, 0.0);
        String classLabel = intent.getStringExtra(SpeechActivity.classLabel);
        float[] recording_buffer = intent.getFloatArrayExtra(SpeechActivity.recording);

        // Capture the layout's TextView and set the string as its text
        TextView textViewProb = findViewById(R.id.textViewrProbabitlity);
        String prediction_probability = String.format("%.2f", probability * 100);
        textViewProb.setText(prediction_probability + " %");

        TextView textViewLabel = findViewById(R.id.textViewLabel);
        String capClassLabel = classLabel.substring(0, 1).toUpperCase() + classLabel.substring(1);
        textViewLabel.setText(capClassLabel);

        // Display the right image depending on the class label
        ImageView imageViewLabel = findViewById(R.id.imageViewLabel);
        if (classLabel.equals("silence")) {
            imageViewLabel.setImageDrawable(getResources().getDrawable(R.drawable.silence_bachground));
        } else if (classLabel.equals("singing")) {
            imageViewLabel.setImageDrawable(getResources().getDrawable(R.drawable.singing_background));
        } else {
            imageViewLabel.setImageDrawable(getResources().getDrawable(R.drawable.speech_background));
        }

        replayButton = (Button) findViewById(R.id.replay_button);
        replayButton.setOnClickListener(
                new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        Log.v(LOG_TAG, "replayRecordedSound");
                        replayRecordedSound(recording_buffer);
                    }
                });
    }

    private void replayRecordedSound(float[] recordedBuffer) {
        int intSize = AudioTrack.getMinBufferSize(48000, AudioFormat.CHANNEL_CONFIGURATION_MONO, AudioFormat.ENCODING_PCM_FLOAT);

        AudioTrack audioTrack = new AudioTrack(AudioManager.STREAM_MUSIC, 48000, AudioFormat.CHANNEL_CONFIGURATION_MONO,
                AudioFormat.ENCODING_PCM_FLOAT, intSize, AudioTrack.MODE_STREAM);
        audioTrack.play();
        audioTrack.write(recordedBuffer, 0, recordedBuffer.length, WRITE_BLOCKING);
        audioTrack.stop();
        audioTrack.release();
    }
}
