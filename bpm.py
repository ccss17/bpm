"""Module for BPM estimating"""

import sys
import multiprocessing as mp

import numpy as np
import librosa
import pretty_midi
import mido


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(midi_path):
    """Function to estimate BPM from mid file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(midi_path)
    return midi_data.estimate_tempo()


def get_bpm_from_midi(midi_path):
    """Function to extract BPM information from midi file"""
    mid = mido.MidiFile(midi_path)
    time_signature = (4, 4)  # default time signature

    if mid.type == 0:
        for msg in mid.tracks[0]:
            if msg.type == "time_signature":
                time_signature = (msg.numerator, msg.denominator)
            elif msg.type == "set_tempo":
                return mido.tempo2bpm(msg.tempo, time_signature=time_signature)
    elif mid.type == 1:
        tempo = 120  # default tempo
        merged_track = mido.merge_tracks(mid.tracks)
        lyric_note_num = 0
        total_lyric_note_num = 0
        tempo_mean_numerator = 0
        first_tempo = True
        for msg in merged_track:
            if msg.type == "note_on" or msg.type == "note_off" or msg.type == "lyrics":
                lyric_note_num += 1
            elif msg.type == "set_tempo":
                if first_tempo:
                    first_tempo = False
                else:
                    tempo_mean_numerator += tempo * lyric_note_num
                    total_lyric_note_num += lyric_note_num
                tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
                lyric_note_num = 0
            elif msg.type == "time_signature":
                time_signature = (msg.numerator, msg.denominator)
            elif msg.type == "end_of_track":
                tempo_mean_numerator += tempo * lyric_note_num
                total_lyric_note_num += lyric_note_num
        return tempo_mean_numerator / total_lyric_note_num
    elif mid.type == 2:
        raise NotImplementedError
    else:
        raise NotImplementedError


def print_track(
    track, mid_file, print_bound_per_track=float("inf"), print_dominant_tempo=False
):
    """print track"""

    def print_lyric_note_num(lyric_note_num):
        print(" " * 8 + f"Total item num: {lyric_note_num}")

    # default setting
    time_signature = (4, 4)
    tempo = 120
    lyric_encode = "utf-8"

    total_time = 0
    total_time2 = 0
    lyric_note_num = 0
    first_tempo = True
    for i, msg in enumerate(track):
        total_time += mido.tick2second(
            msg.time, ticks_per_beat=mid_file.ticks_per_beat, tempo=tempo
        )
        total_time2 += msg.time
        if i > print_bound_per_track:
            continue
        if msg.type == "note_on":
            lyric_note_num += 1
            if not print_dominant_tempo:
                print(
                    f"{i:4} ┌note on ┐ {pretty_midi.note_number_to_name(msg.note)} ({msg})",
                )
        elif msg.type == "note_off":
            lyric_note_num += 1
            if not print_dominant_tempo:
                print(
                    f"{i:4} └note off┘ {pretty_midi.note_number_to_name(msg.note)} ({msg})",
                )
        elif msg.type == "set_tempo":
            if not first_tempo:
                print_lyric_note_num(lyric_note_num)
            else:
                first_tempo = False
            tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
            print(f"{i:4} [Tempo] BPM={tempo} (time={msg.time})")
            lyric_note_num = 0
        elif msg.type == "end_of_track":
            print_lyric_note_num(lyric_note_num)
            print(f"{i:4} [End of Track] (time={msg.time})")
        elif msg.type == "lyrics":
            lyric_note_num += 1
            if not print_dominant_tempo:
                try:
                    print(
                        f"{i:4} │ lyrics │ {msg.bin()[3:].decode(lyric_encode)} (time={msg.time})",
                    )
                except UnicodeDecodeError:
                    lyric_encode = "euc-kr"
        elif msg.type == "channel_prefix":
            print(f"{i:4} [Channel Prefix] channel={msg.channel} (time={msg.time})")
        elif msg.type == "track_name":
            pass  # Track information was already printed
            # print("[Track name]", msg, msg.bin()[3:].decode(lyric_encode))
        elif msg.type == "instrument_name":
            print(f"{i:4} [Instrument Name] {msg.name} (time={msg.time})")
        elif msg.type == "smpte_offset":
            print(f"{i:4} [SMPTE] {msg}")
        elif msg.type == "key_signature":
            print(f"{i:4} [Key Signature] {msg.key} (time={msg.time})")
        elif msg.type == "time_signature":
            print(
                f"{i:4} [Time Signature] {msg.numerator}/{msg.denominator} "
                + f"(clocks_per_click={msg.clocks_per_click}, "
                + f"notated_32nd_notes_per_beat={msg.notated_32nd_notes_per_beat}, "
                + f"time={msg.time})",
            )
            time_signature = (msg.numerator, msg.denominator)
        else:
            print(i, msg)
    # print("(test)total ticks", total_time)
    # print("(test)total ticks2", total_time2)
    print("lyric encode:", lyric_encode)


def analysis_midi(
    midi_path,
    print_bound_per_track=float("inf"),
    print_dominant_tempo=False,
    convert_1_to_0=False,
):
    """Function to analysis mid file
    ref: https://mido.readthedocs.io/en/stable/files/midi.html
    """
    sys.stdout.reconfigure(encoding="utf-8")  # printing encoding

    # print header information of midi file
    mid = mido.MidiFile(midi_path)
    print("[MIDI File Header]")
    print("mid file type:", mid.type)
    print("ticks per beat:", mid.ticks_per_beat)
    print("total duration:", mid.length)

    if mid.type == 1 and convert_1_to_0:
        mid.tracks = [mido.merge_tracks(mid.tracks)]

    for i, track in enumerate(mid.tracks):
        print(f"\nTrack {i}: {track.name}\n")
        print_track(track, mid, print_bound_per_track, print_dominant_tempo)


def estimated_bpm_error(audio_path, midi_path):
    """Function to calculate error of estimated bpm"""
    estimated_bpm = bpm_estimator_librosa(audio_path)[0]
    bpm_from_midi_file = get_bpm_from_midi(midi_path)

    error = abs(estimated_bpm - bpm_from_midi_file)
    corrected_overestimated_bpm_error_8 = abs(estimated_bpm / 8 - bpm_from_midi_file)
    corrected_overestimated_bpm_error_4 = abs(estimated_bpm / 4 - bpm_from_midi_file)
    corrected_overestimated_bpm_error_2 = abs(estimated_bpm / 2 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_2 = abs(estimated_bpm * 2 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_4 = abs(estimated_bpm * 4 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_8 = abs(estimated_bpm * 8 - bpm_from_midi_file)

    corrected_error_2 = min(
        error, corrected_overestimated_bpm_error_2, corrected_underestimated_bpm_error_2
    )
    corrected_error_4 = min(
        error,
        corrected_overestimated_bpm_error_4,
        corrected_overestimated_bpm_error_2,
        corrected_underestimated_bpm_error_2,
        corrected_underestimated_bpm_error_4,
    )
    corrected_error_8 = min(
        error,
        corrected_overestimated_bpm_error_8,
        corrected_overestimated_bpm_error_4,
        corrected_overestimated_bpm_error_2,
        corrected_underestimated_bpm_error_2,
        corrected_underestimated_bpm_error_4,
        corrected_underestimated_bpm_error_8,
    )
    return (
        error,
        corrected_error_2,
        corrected_error_4,
        corrected_error_8,
    )


def statistics_estimated_bpm_error(path_obj):
    """Function to get statistics of errors of estimated bpm
    by multiprocessing"""

    with mp.Pool(mp.cpu_count()) as p:
        error_array = np.array(
            p.starmap(
                estimated_bpm_error,
                zip(path_obj.rglob("*.wav"), path_obj.rglob("*.mid")),
            )
        )

    print(f"{np.mean(error_array[:, 0]):5.2f}, {np.std(error_array[:, 0]):5.2f}")
    print(f"{np.mean(error_array[:, 1]):5.2f}, {np.std(error_array[:, 1]):5.2f}")
    print(f"{np.mean(error_array[:, 2]):5.2f}, {np.std(error_array[:, 2]):5.2f}")
    print(f"{np.mean(error_array[:, 3]):5.2f}, {np.std(error_array[:, 3]):5.2f}")
