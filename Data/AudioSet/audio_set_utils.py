from errors import SubprocessError, FfmpegValidationError, \
                   FfmpegIncorrectDurationError, FfmpegUnopenableFileError

import collections
import os
import re

import sox
import soundfile as sf
import subprocess as sp

HTTP_ERR_PATTERN = re.compile(r'Server returned (4|5)(X|[0-9])(X|[0-9])')


def ffmpeg(ffmpeg_path, input_path, output_path, input_args=None,
           output_args=None, log_level='error', num_retries=10,
           validation_callback=None, validation_args=None):
    """
    Transform an input file using `ffmpeg`
    Args:
        ffmpeg_path:  Path to ffmpeg executable
                      (Type: str)
        input_path:   Path/URL to input file(s)
                      (Type: str or iterable)
        output_path:  Path/URL to output file
                      (Type: str)
        input_args:   Options/flags for input files
                      (Type: list[str])
        output_args:  Options/flags for output files
                      (Type: list[str])
        log_level:    ffmpeg logging level
                      (Type: str)
        num_retries:  Number of retries if ffmpeg encounters an HTTP issue
                      (Type: int)
    """
    if type(input_path) == str:
        inputs = ['-i', input_path]
    elif isinstance(input_path, collections.Iterable):
        inputs = []
        for path in input_path:
            inputs.append('-i')
            inputs.append(path)
    else:
        error_msg = '"input_path" must be a str or an iterable, but got type {}'
        raise ValueError(error_msg.format(str(type(input_path))))

    if not input_args:
        input_args = []
    if not output_args:
        output_args = []

    last_err = None
    for attempt in range(num_retries):
        try:
            args = [ffmpeg_path] + input_args + inputs + output_args + [output_path, '-loglevel', log_level]
            run_command(args)

            # Validate if a callback was passed in
            if validation_callback is not None:
                validation_args = validation_args or {}
                validation_callback(output_path, **validation_args)
            break
        except SubprocessError as e:
            last_err = e
            stderr = e.cmd_stderr.rstrip()
            if stderr.endswith('already exists. Exiting.'):
                print('ffmpeg output file "{}" already exists.'.format(output_path))
                break
            elif HTTP_ERR_PATTERN.match(stderr):
                # Retry if we got a 4XX or 5XX, in case it was just a network issue
                continue

            print(str(e) + '. Retrying...')
            if os.path.exists(output_path):
                os.remove(output_path)

        except FfmpegIncorrectDurationError as e:
            last_err = e
            if attempt < num_retries - 1 and os.path.exists(output_path):
                os.remove(output_path)
            # If the duration of the output audio is different, alter the
            # duration argument to account for this difference and try again
            duration_diff = e.target_duration - e.actual_duration
            try:
                duration_idx = input_args.index('-t') + 1
                input_args[duration_idx] = str(float(input_args[duration_idx]) + duration_diff)
            except ValueError:
                duration_idx = output_args.index('-t') + 1
                output_args[duration_idx] = str(float(output_args[duration_idx]) + duration_diff)

            print(str(e) + '; Retrying...')
            continue

        except FfmpegUnopenableFileError as e:
            last_err = e
            # Always remove unopenable files
            if os.path.exists(output_path):
                os.remove(output_path)
            # Retry if the output did not validate
            print('ffmpeg output file "{}" could not be opened: {}. Retrying...'.format(output_path, e.open_error))
            continue

        except FfmpegValidationError as e:
            last_err = e
            if attempt < num_retries - 1 and os.path.exists(output_path):
                os.remove(output_path)
            # Retry if the output did not validate
            print('ffmpeg output file "{}" did not validate: {}. Retrying...'.format(output_path, e))
            continue
    else:
        error_msg = 'Maximum number of retries ({}) reached. Could not obtain inputs at {}. Error: {}'
        print(error_msg.format(num_retries, input_path, str(last_err)))


def validate_audio(audio_filepath, audio_info, end_past_video_end=False):
    """
    Take audio file and sanity check basic info.
        Sample output from sox:
            {
                'bitrate': 16,
                'channels': 2,
                'duration': 9.999501,
                'encoding': 'FLAC',
                'num_samples': 440978,
                'sample_rate': 44100.0,
                'silent': False
            }
    Args:
        audio_filepath:   Path to output audio
                          (Type: str)
        audio_info:       Audio info dict
                          (Type: dict[str, *])
    Returns:
        check_passed:  True if sanity check passed
                       (Type: bool)
    """
    if not os.path.exists(audio_filepath):
        error_msg = 'Output file {} does not exist.'.format(audio_filepath)
        raise FfmpegValidationError(error_msg)

    # Check to see if we can open the file
    try:
        sf.read(audio_filepath)
    except Exception as e:
        raise FfmpegUnopenableFileError(audio_filepath, e)

    sox_info = sox.file_info.info(audio_filepath)

    # If duration specifically doesn't match, catch that separately so we can
    # retry with a different duration
    target_duration = audio_info['duration']
    actual_duration = sox_info['num_samples'] / audio_info['sample_rate']
    if target_duration != actual_duration:
        if not(end_past_video_end and actual_duration < target_duration):
            raise FfmpegIncorrectDurationError(audio_filepath, target_duration,
                                               actual_duration)
    for k, v in audio_info.items():
        if k == 'duration' and (end_past_video_end and actual_duration < target_duration):
            continue

        output_v = sox_info[k]
        if v != output_v:
            error_msg = 'Output audio {} should have {} = {}, but got {}.'.format(audio_filepath, k, v, output_v)
            raise FfmpegValidationError(error_msg)


def run_command(cmd, **kwargs):
    """
    Run a command line command
    Args:
        cmd:       List of strings used in the command
                   (Type: list[str])
        **kwargs:  Keyword arguments to be passed to subprocess.Popen()
    Returns:
        stdout:       stdout string produced by running command
                      (Type: str)
        stderr:       stderr string produced by running command
                      (Type: str)
        return_code:  Exit/return code from running command
                      (Type: int)
    """
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, **kwargs)
    stdout, stderr = proc.communicate()

    return_code = proc.returncode

    if return_code != 0:
        raise SubprocessError(cmd, return_code, stdout.decode(), stderr.decode())

    return stdout, stderr, return_code