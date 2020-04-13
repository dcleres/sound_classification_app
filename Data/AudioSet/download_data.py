import pandas as pd
import os
import pafy
from tqdm import tqdm

from audio_set_utils import ffmpeg, validate_audio


def common_member(a, b):
    a_set = set(a)
    b_set = set(b)
    if a_set & b_set:
        return True
    else:
        return False


def has_no_common_member(a, b, c, d):
    a_set = set(a)
    b_set = set(b)
    c_set = set(c)
    d_set = set(d)
    if (a_set & b_set) and ((a_set & c_set) or (a_set & d_set)):
        return False
    elif (a_set & b_set) or ((a_set & c_set) and (a_set & d_set)):
        return False
    else:
        return True


def get_media_filename(ytid, ts_start, ts_end):
    """
    Get the filename (without extension) for a media file (audio or video) for a YouTube video segment
    Args:
        ytid:      YouTube ID of a video
                   (Type: str)
        ts_start:  Segment start time (in seconds)
                   (Type: float or int)
        ts_end:    Segment end time (in seconds)
                   (Type: float or int)
    Returns:
        media_filename:  Filename (without extension) for segment media file
                         (Type: str)
    """
    tms_start, tms_end = int(ts_start * 1000), int(ts_end * 1000)
    return "{}_{}_{}".format(ytid, tms_start, tms_end)


def download_yt_video(
    ytid,
    ts_start,
    ts_end,
    output_dir,
    ffmpeg_path,
    label,
    audio_codec="flac",
    audio_format="flac",
    audio_sample_rate=48000,
    audio_bit_depth=16,
    num_retries=10,
):
    """
    Download a Youtube video (with the audio and video separated).
    The audio will be saved in <output_dir>/audio and the video will be saved in
    <output_dir>/video.
    The output filename is of the format:
        <YouTube ID>_<start time in ms>_<end time in ms>.<extension>
    Args:
        ytid:          Youtube ID string
                       (Type: str)
        ts_start:      Segment start time (in seconds)
                       (Type: float)
        ts_start:      Segment end time (in seconds)
                       (Type: float)
        output_dir:    Output directory where video will be saved
                       (Type: str)
        ffmpeg_path:   Path to ffmpeg executable
                       (Type: str)
    Keyword Args:
        audio_codec:        Name of audio codec used by ffmpeg to encode
                            output audio
                            (Type: str)
        audio_format:       Name of audio container format used for output audio
                            (Type: str)
        audio_sample_rate:  Target audio sample rate (in Hz)
                            (Type: int)
        audio_bit_depth:    Target audio sample bit depth
                            (Type: int)
        num_retries:        Number of attempts to download and process an audio
                            or video file with ffmpeg
                            (Type: int)
    Returns:
        audio_filepath:  Filepath to audio file
                         (Type: str)
    """
    # Compute some things from the segment boundaries
    duration = ts_end - ts_start

    # Make the output format and video URL
    # Output format is in the format:
    #   <YouTube ID>_<start time in ms>_<end time in ms>.<extension>
    media_filename = get_media_filename(ytid, ts_start, ts_end)
    audio_filepath = os.path.join(output_dir, "audio", label, media_filename + "." + audio_format)
    video_page_url = "https://www.youtube.com/watch?v={}".format(ytid)

    # Get the direct URLs to the videos with best audio and with best video (with audio)
    try:
        video = pafy.new(video_page_url)
        video_duration = video.length
    except OSError or AttributeError:
        return None

    end_past_video_end = False
    if ts_end > video_duration:
        warn_msg = "End time for segment ({} - {}) of video {} extends past end of video (length {} sec)"
        print(warn_msg.format(ts_start, ts_end, ytid, video_duration))
        duration = video_duration - ts_start
        ts_end = ts_start + duration
        end_past_video_end = True

    best_audio = video.getbestaudio()
    try:
        best_audio_url = best_audio.url
    except AttributeError:
        return None

    audio_info = {
        "sample_rate": audio_sample_rate,
        "channels": 2,
        "bitrate": audio_bit_depth,
        "encoding": audio_codec.upper(),
        "duration": duration,
    }

    # Download the audio
    audio_input_args = ["-n", "-ss", str(ts_start)]
    audio_output_args = [
        "-t",
        str(duration),
        "-ar",
        str(audio_sample_rate),
        "-vn",
        "-ac",
        str(audio_info["channels"]),
        "-sample_fmt",
        "s{}".format(audio_bit_depth),
        "-f",
        audio_format,
        "-acodec",
        audio_codec,
    ]
    ffmpeg(
        ffmpeg_path,
        best_audio_url,
        audio_filepath,
        input_args=audio_input_args,
        output_args=audio_output_args,
        num_retries=num_retries,
        validation_callback=validate_audio,
        validation_args={"audio_info": audio_info, "end_past_video_end": end_past_video_end},
    )

    print("Downloaded audio {} ({} - {})".format(ytid, ts_start, ts_end))

    return audio_filepath


if __name__ == "__main__":

    nb_samples = 3000  # number of samples to select from the AudioSet dataset

    csv_file = "unbalanced_train_segments.csv"
    # Allow only official CSV files as no audio paths are defined otherwise
    assert csv_file in ["eval_segments.csv", "balanced_train_segments.csv", "unbalanced_train_segments.csv"]

    # Get the desired filenames and categories
    df = pd.read_csv(csv_file, skiprows=2, sep=", ", engine="python")

    label_id_csv = pd.read_csv("class_labels_indices.csv")

    # Convert my selected labels to ID
    # the selected labels are those which make the most sense for the recognition of singing, speaking, and silence.
    audio_labels_speech = [
        "Speech",
        "Male speech, man speaking",
        "Female speech, woman speaking",
        "Child speech, kid speaking",
        "Conversation",
        "Narration, monologue",
        "Speech synthesizer",
    ]
    audio_labels_singing = [
        "Singing",
        "Choir",
        "Yodeling",
        "Chant",
        "Male singing",
        "Female singing",
        "Child singing",
        "Synthetic singing",
        "Rapping",
    ]
    audio_labels_silence = ["Breathing", "Walk, footsteps", "Silence"]

    all_selected_labels = audio_labels_speech + audio_labels_singing + audio_labels_silence

    singing_label_ids = []
    for label in audio_labels_singing:
        singing_label_ids.append(label_id_csv[label_id_csv.display_name == label].mid.values[0])

    speech_label_ids = []
    for label in audio_labels_speech:
        speech_label_ids.append(label_id_csv[label_id_csv.display_name == label].mid.values[0])

    silence_label_ids = []
    for label in audio_labels_silence:
        silence_label_ids.append(label_id_csv[label_id_csv.display_name == label].mid.values[0])

    label_ids = []
    for label in all_selected_labels:
        label_ids.append(label_id_csv[label_id_csv.display_name == label].mid.values[0])

    df["is_interesting_label"] = df.positive_labels.apply(
        lambda x: common_member(x.replace('"', "").split(","), label_ids)
    )
    df_with_interesting_labels = df[df.is_interesting_label==True]

    # Discard data with overlapping classes
    df_with_interesting_labels["does_not_overlap"] = df_with_interesting_labels.positive_labels.apply(
        lambda x: has_no_common_member(
            x.replace('"', "").split(","), audio_labels_speech, audio_labels_silence, audio_labels_singing
        )
    )
    df_with_interesting_labels[df_with_interesting_labels["does_not_overlap"]==True]

    # Split data
    df_with_interesting_labels["is_silence"] = df_with_interesting_labels.positive_labels.apply(
        lambda x: common_member(x.replace('"', "").split(","), silence_label_ids)
    )
    df_with_interesting_labels["is_speech"] = df_with_interesting_labels.positive_labels.apply(
        lambda x: common_member(x.replace('"', "").split(","), speech_label_ids)
    )
    df_with_interesting_labels["is_singing"] = df_with_interesting_labels.positive_labels.apply(
        lambda x: common_member(x.replace('"', "").split(","), singing_label_ids)
    )

    df_speech_data = df_with_interesting_labels[df_with_interesting_labels.is_speech==True]
    df_silence_data = df_with_interesting_labels[df_with_interesting_labels.is_silence==True]
    df_singing_data = df_with_interesting_labels[df_with_interesting_labels.is_singing==True]

    df_singing_data_sampled = df_singing_data.sample(n=nb_samples, random_state=1)
    df_speech_data_sampled = df_speech_data.sample(n=nb_samples, random_state=1)
    df_silence_data_sampled = df_silence_data.sample(n=nb_samples, random_state=1)

    df_speech_data_sampled.to_csv("audio/speech_data_sampled.csv", index=False)
    df_singing_data_sampled.to_csv("audio/singing_data_sampled.csv", index=False)
    df_silence_data_sampled.to_csv("audio/silence_data_sampled.csv", index=False)

    ## Download the audio files
    output_dir = "/Users/dcleres/sound_classification_app/Data/AudioSet"
    ffmpeg_path = "/usr/local/bin/ffmpeg"

    obtained_singing_audio_list = []
    for ytid, ts_start, ts_end in tqdm(df_singing_data_sampled[["# YTID", "start_seconds", "end_seconds"]].values):
        obtained_singing_audio_list.append(
            download_yt_video(ytid, ts_start, ts_end, output_dir, ffmpeg_path, "singing")
        )

    obtained_speech_audio_list = []
    for ytid, ts_start, ts_end in tqdm(df_speech_data_sampled[["# YTID", "start_seconds", "end_seconds"]].values):
        obtained_speech_audio_list.append(download_yt_video(ytid, ts_start, ts_end, output_dir, ffmpeg_path, "speech"))

    obtained_silence_audio_list = []
    for ytid, ts_start, ts_end in tqdm(df_silence_data_sampled[["# YTID", "start_seconds", "end_seconds"]].values):
        obtained_silence_audio_list.append(
            download_yt_video(ytid, ts_start, ts_end, output_dir, ffmpeg_path, "silence")
        )
