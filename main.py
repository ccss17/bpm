"""Module for BPM estimating"""

import sys
import pathlib
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
        for track in mid.tracks:
            for msg in track:
                if msg.type == "time_signature":
                    time_signature = (msg.numerator, msg.denominator)
                elif msg.type == "set_tempo":
                    return mido.tempo2bpm(msg.tempo, time_signature=time_signature)


def print_track(
    track, mid_file, print_bound_per_track=float("inf"), print_dominant_tempo=False
):
    """print track"""
    # default setting
    time_signature = (4, 4)
    tempo = 120
    lyric_encode = "utf-8"

    total_time = 0
    total_time2 = 0
    item_num = 0
    for i, msg in enumerate(track):
        total_time += mido.tick2second(
            msg.time, ticks_per_beat=mid_file.ticks_per_beat, tempo=tempo
        )
        total_time2 += msg.time
        if i > print_bound_per_track:
            continue
        if msg.type == "note_on":
            item_num += 1
            if not print_dominant_tempo:
                print(
                    f"{i:4} ┌note on ┐ {pretty_midi.note_number_to_name(msg.note)} ({msg})",
                )
        elif msg.type == "note_off":
            item_num += 1
            if not print_dominant_tempo:
                print(
                    f"{i:4} └note off┘ {pretty_midi.note_number_to_name(msg.note)} ({msg})",
                )
        elif msg.type == "end_of_track":
            print(f"{i:4} [End of Track] (time={msg.time})")
        elif msg.type == "lyrics":
            item_num += 1
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
        elif msg.type == "set_tempo":
            if print_dominant_tempo:
                print(" " * 8 + f"Total item num: {item_num}")
            tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
            print(f"{i:4} [Tempo] BPM={tempo} (time={msg.time})")
            item_num = 0
        else:
            print(i, msg)
    print("(test)total ticks", total_time)
    print("(test)total ticks2", total_time2)
    print("lyric encode:", lyric_encode)


def analysis_midi(midi_path, print_bound_per_track=float("inf")):
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

    for i, track in enumerate(mid.tracks):
        print(f"\nTrack {i}: {track.name}\n")
        print_track(track, mid, print_bound_per_track)


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(midi_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpm_estimator_pretty_midi(midi_path)))


def test_get_bpm_from_midi(midi_path):
    """Test get_bpm_from_midi"""
    print(round(get_bpm_from_midi(midi_path)))


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

    print(np.mean(error_array[:, 0]), np.std(error_array[:, 0]))
    print(np.mean(error_array[:, 1]), np.std(error_array[:, 1]))
    print(np.mean(error_array[:, 2]), np.std(error_array[:, 2]))
    print(np.mean(error_array[:, 3]), np.std(error_array[:, 3]))


def test_convert_midi_format_1_to_0(midi_path):
    """test
    ref: https://stackoverflow.com/questions/55431137/
    how-to-convert-midi-type-1-files-to-midi-type-0-in-python-or-command-line"""
    mid = mido.MidiFile(midi_path)
    mido.merge_tracks(mid.tracks)
    print_track(mido.merge_tracks(mid.tracks), mid, print_dominant_tempo=True)


if __name__ == "__main__":
    samples = [
        {
            "wav": "sample/SINGER_66_30TO49_HUSKY_MALE_DANCE_C2835.wav",
            "mid": "sample/SINGER_66_30TO49_HUSKY_MALE_DANCE_C2835.mid",
        },
        {
            "wav": "sample/SINGER_16_10TO29_CLEAR_FEMALE_BALLAD_C0632.wav",
            "mid": "sample/SINGER_16_10TO29_CLEAR_FEMALE_BALLAD_C0632.mid",
        },
        {
            "wav": "sample/ba_05688_-4_a_s02_m_02.wav",
            "mid": "sample/ba_05688_-4_a_s02_m_02.mid",
        },
        {
            "wav": "sample/ba_09303_+0_a_s02_m_02.wav",
            "mid": "sample/ba_09303_+0_a_s02_m_02.mid",
        },
    ]

    # test_bpm_estimator_librosa(samples[0]["wav"])
    # test_bpm_estimator_pretty_midi(samples[0]["mid"])
    # test_get_bpm_from_midi(samples[0]["mid"])

    # for sample in samples:
    #     print(
    #         f'{bpm_estimator_librosa(sample["wav"])[0]:.2f}'
    #         + f' {bpm_estimator_pretty_midi(sample["mid"]):.2f}'
    #         + f' {get_bpm_from_midi(sample["mid"]):.2f}'
    #     )

    # print(bpm_estimator_librosa(samples[2]["wav"])[0])

    # analysis_midi(samples[0]["mid"], print_bound_per_track=25)
    # analysis_midi(samples[2]["mid"], print_bound_per_track=40)
    # analysis_midi(samples[3]["mid"], print_bound_per_track=20)
    # analysis_midi(samples[0]["mid"])
    # analysis_midi(samples[1]["mid"])
    # analysis_midi(samples[2]["mid"])
    # analysis_midi(samples[3]["mid"])

    # print()

    # test_convert_midi_format_1_to_0(samples[2]["mid"])
    data_path = pathlib.Path("dataset/가창자_s02")
    for i, mid_path in enumerate(data_path.rglob("*.mid")):
        if i == 4:
            test_convert_midi_format_1_to_0(mid_path)
            print()
            print(mid_path)

    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # data_path = pathlib.Path("d:/dataset/177.다음색 가이드보컬 데이터")
    # data_path = pathlib.Path("dataset/SINGER_16")
    # data_path = pathlib.Path("dataset/가창자_s02")
    # statistics_estimated_bpm_error(data_path)
