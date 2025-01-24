"""Module for BPM estimating"""

import multiprocessing as mp
import random

import numpy as np
import librosa
import pretty_midi
import mido

from rich import print as rprint

from note import (
    DEFAULT_BPM,
    DEFAULT_TIME_SIGNATURE,
)


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(midi_path):
    """Function to estimate BPM from mid file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(midi_path)
    return midi_data.estimate_tempo()


def _bpm_from_midi_format_0(mid_obj):
    time_signature = DEFAULT_TIME_SIGNATURE  # default time signature
    for msg in mid_obj.tracks[0]:
        if msg.type == "time_signature":
            time_signature = (msg.numerator, msg.denominator)
        elif msg.type == "set_tempo":
            return mido.tempo2bpm(msg.tempo, time_signature=time_signature)


def _bpm_from_midi_format_1(mid_obj):
    bpm = DEFAULT_BPM
    time_signature = DEFAULT_TIME_SIGNATURE
    # convert midi format 1 to 0
    merged_track = mido.merge_tracks(mid_obj.tracks)
    lyric_note_num = 0
    total_lyric_note_num = 0
    tempo_mean_numerator = 0
    first_tempo = True
    for msg in merged_track:
        if (
            msg.type == "note_on"
            or msg.type == "note_off"
            or msg.type == "lyrics"
        ):
            lyric_note_num += 1
        elif msg.type == "set_tempo":
            if first_tempo:
                first_tempo = False
            else:
                tempo_mean_numerator += bpm * lyric_note_num
                total_lyric_note_num += lyric_note_num
            bpm = round(
                mido.tempo2bpm(msg.tempo, time_signature=time_signature)
            )
            lyric_note_num = 0
        elif msg.type == "time_signature":
            time_signature = (msg.numerator, msg.denominator)
        elif msg.type == "end_of_track":
            tempo_mean_numerator += bpm * lyric_note_num
            total_lyric_note_num += lyric_note_num
    return tempo_mean_numerator / total_lyric_note_num


def bpm_from_midi(mid_obj):
    """Function to extract BPM information from midi file"""
    if mid_obj.type == 0:
        return _bpm_from_midi_format_0(mid_obj)
    elif mid_obj.type == 1:
        return _bpm_from_midi_format_1(mid_obj)
    elif mid_obj.type == 2:
        raise NotImplementedError
    else:
        raise NotImplementedError


def bpm_from_midi_file(midi_path):
    """Function to extract BPM information from midi file"""
    mid = mido.MidiFile(midi_path)
    return bpm_from_midi(mid)


def estimated_bpm_error(audio_path, midi_path):
    """Function to calculate error of estimated bpm"""
    if not midi_path.name.split(".")[0] == audio_path.name.split(".")[0]:
        raise ValueError
    estimated_bpm = bpm_estimator_librosa(audio_path)[0]
    bpm = bpm_from_midi_file(midi_path)

    error = abs(estimated_bpm - bpm)
    corrected_overestimated_bpm_error_8 = abs(estimated_bpm / 8 - bpm)
    corrected_overestimated_bpm_error_4 = abs(estimated_bpm / 4 - bpm)
    corrected_overestimated_bpm_error_2 = abs(estimated_bpm / 2 - bpm)
    corrected_underestimated_bpm_error_2 = abs(estimated_bpm * 2 - bpm)
    corrected_underestimated_bpm_error_4 = abs(estimated_bpm * 4 - bpm)
    corrected_underestimated_bpm_error_8 = abs(estimated_bpm * 8 - bpm)

    selected_error = np.argmin(
        [
            corrected_overestimated_bpm_error_8,
            corrected_overestimated_bpm_error_4,
            corrected_overestimated_bpm_error_2,
            error,
            corrected_underestimated_bpm_error_2,
            corrected_underestimated_bpm_error_4,
            corrected_underestimated_bpm_error_8,
        ]
    )

    corrected_error_2 = min(
        error,
        corrected_overestimated_bpm_error_2,
        corrected_underestimated_bpm_error_2,
    )
    corrected_error_4 = min(
        corrected_error_2,
        corrected_overestimated_bpm_error_4,
        corrected_underestimated_bpm_error_4,
    )
    corrected_error_8 = min(
        corrected_error_4,
        corrected_overestimated_bpm_error_8,
        corrected_underestimated_bpm_error_8,
    )
    return (
        error,
        corrected_error_2,
        corrected_error_4,
        corrected_error_8,
        selected_error,
    )


def statistics_estimated_bpm_error(path_obj, sample_num=None):
    """Function to get statistics of errors of estimated bpm
    by multiprocessing"""

    with mp.Pool(mp.cpu_count()) as p:
        samples = zip(
            sorted(path_obj.rglob("*.wav")), sorted(path_obj.rglob("*.mid"))
        )
        if sample_num:
            samples = list(samples)
            if sample_num < len(samples):
                samples = random.sample(samples, k=sample_num)
        error_array = np.array(p.starmap(estimated_bpm_error, samples))

    rprint(
        f"error(0); mean/std: {np.mean(error_array[:, 0]):5.2f}, "
        + f"{np.std(error_array[:, 0]):5.2f}"
    )
    rprint(
        f"error(2); mean/std: {np.mean(error_array[:, 1]):5.2f}, "
        + f"{np.std(error_array[:, 1]):5.2f}"
    )
    rprint(
        f"error(4); mean/std: {np.mean(error_array[:, 2]):5.2f}, "
        + f"{np.std(error_array[:, 2]):5.2f}"
    )
    rprint(
        f"error(8); mean/std: {np.mean(error_array[:, 3]):5.2f}, "
        + f"{np.std(error_array[:, 3]):5.2f}"
    )

    selected_error_frequencies = np.bincount(
        error_array[:, 4].astype(np.int64)
    )
    selected_error_frequencies = np.pad(
        selected_error_frequencies,
        (0, 7 - selected_error_frequencies.shape[0]),
        "constant",
        constant_values=(0, 0),
    )
    rprint("selected error:")
    rprint(f"  error(/8): {selected_error_frequencies[0]}")
    rprint(f"  error(/4): {selected_error_frequencies[1]}")
    rprint(f"  error(/2): {selected_error_frequencies[2]}")
    rprint(f"  error(0) : {selected_error_frequencies[3]}")
    rprint(f"  error(*2): {selected_error_frequencies[4]}")
    rprint(f"  error(*4): {selected_error_frequencies[5]}")
    rprint(f"  error(*8): {selected_error_frequencies[6]}")
