"""Module for test code"""

import pathlib

import mido

import bpmlib


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpmlib.bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(midi_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpmlib.bpm_estimator_pretty_midi(midi_path)))


def test_get_bpm_from_midi(midi_path):
    """Test get_bpm_from_midi"""
    print(round(bpmlib.get_bpm_from_midi(midi_path)))


def test_convert_midi_format_1_to_0(midi_path, blind_note_lyrics=True):
    """test
    ref: https://stackoverflow.com/questions/55431137/
    how-to-convert-midi-type-1-files-to-midi-type-0-in-python-or-command-line"""
    mid = mido.MidiFile(midi_path)
    merged_track = mido.merge_tracks(mid.tracks)
    print(f"\nTrack 0: {merged_track.name}\n")
    bpmlib.print_track(merged_track, mid, blind_note_lyrics=blind_note_lyrics)


def test_create_sample_midi1(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.Message("note_on", note=74, velocity=64, time=4))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))
    track.append(mido.MetaMessage("end_of_track", time=8))

    mid.save(midi_path)


def test_create_sample_midi2(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="a", time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="b", time=4))
    track.append(mido.Message("note_on", note=74, velocity=64, time=4))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="d", time=4))

    mid.save(midi_path)


def test_create_sample_midi3(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="a", time=6))
    track.append(mido.MetaMessage("lyrics", text="b", time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))

    mid.save(midi_path)


def test_create_sample_midi4(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=64, time=2))
    track.append(mido.MetaMessage("lyrics", text="a", time=12))
    track.append(mido.Message("note_on", note=74, velocity=64, time=2))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="b", time=10))
    track.append(mido.Message("note_off", note=74, velocity=127, time=8))

    mid.save(midi_path)


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

    #
    # BPM ESTIMATOR vs BPM FROM MIDI
    #
    # test_bpm_estimator_librosa(samples[0]["wav"])
    # test_bpm_estimator_pretty_midi(samples[0]["mid"])
    # test_get_bpm_from_midi(samples[0]["mid"])

    # for sample in samples:
    #     print(
    #         f'{bpmlib.bpm_estimator_librosa(sample["wav"])[0]:.2f}'
    #         + f' {bpmlib.bpm_estimator_pretty_midi(sample["mid"]):.2f}'
    #         + f' {bpmlib.get_bpm_from_midi(sample["mid"]):.2f}'
    #     )

    #
    # ANALYSIS MIDI FILE
    #
    # bpmlib.analysis_midi(samples[0]["mid"], print_bound_per_track=15)
    # bpmlib.analysis_midi(samples[2]["mid"], print_bound_per_track=40)
    # bpmlib.analysis_midi(samples[3]["mid"], print_bound_per_track=20)
    # bpmlib.analysis_midi(samples[0]["mid"])
    # bpmlib.analysis_midi(samples[1]["mid"])
    # bpmlib.analysis_midi(samples[2]["mid"])

    #
    # CONVERT MIDI FORMAT 1 TO 0
    #
    # bpmlib.analysis_midi(samples[3]["mid"], blind_note_lyrics=True, convert_1_to_0=True)
    # bpmlib.analysis_midi(
    #     samples[3]["mid"], blind_note_lyrics=False, convert_1_to_0=True
    # )
    # data_path = pathlib.Path("dataset/가창자_s02")
    # for i, mid_path in enumerate(data_path.rglob("*.mid")):
    #     if i == 4:
    #         test_convert_midi_format_1_to_0(mid_path, blind_note_lyrics=True)

    #
    # CREATE SAMPLE MIDI AND ANALYSIS IT
    #
    # test_create_sample_midi1("test_sample1.mid")
    # bpmlib.analysis_midi("test_sample1.mid")
    # bpmlib.midi2wav("test_sample1.mid", "test_sample1.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi2("test_sample2.mid")
    # bpmlib.analysis_midi("test_sample2.mid")
    # bpmlib.midi2wav("test_sample2.mid", "test_sample2.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi3("test_sample3.mid")
    # bpmlib.analysis_midi("test_sample3.mid")
    # bpmlib.midi2wav("test_sample3.mid", "test_sample3.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi4("test_sample4.mid")
    # bpmlib.analysis_midi("test_sample4.mid")
    # bpmlib.midi2wav("test_sample4.mid", "test_sample4.wav", 60)

    #
    # GET STATISTICS of ESTIMATED CORRECTED BPM ERROR
    #
    # sample_num = 10
    # data_path = pathlib.Path("dataset/SINGER_16")
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path, sample_num=sample_num)
    # print()
    # data_path = pathlib.Path("dataset/가창자_s02")
    # bpmlib.statistics_estimated_bpm_error(data_path)

    # data_path = pathlib.Path("d:/dataset/177.다음색 가이드보컬 데이터")
    # print(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # print()
    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # print(data_path)
    # bpmlib.statistics_estimated_bpm_error(data_path)
    # Output:
    # d:\dataset\177.다음색 가이드보컬 데이터
    # error(0); mean/std: 42.13, 35.27
    # error(2); mean/std:  4.39,  7.71
    # error(4); mean/std:  4.08,  6.77
    # error(8); mean/std:  4.08,  6.77
    # selected error:
    #   error(/8): 0
    #   error(/4): 41
    #   error(/2): 1998
    #   error(0) : 1541
    #   error(*2): 29
    #   error(*4): 0
    #   error(*8): 0

    # d:\dataset\004.다화자 가창 데이터
    # error(0); mean/std: 38.97, 36.49
    # error(2); mean/std:  6.16,  8.72
    # error(4); mean/std:  5.91,  8.17
    # error(8); mean/std:  5.91,  8.17
    # selected error:
    #   error(/8): 0
    #   error(/4): 78
    #   error(/2): 1993
    #   error(0) : 2078
    #   error(*2): 77
    #   error(*4): 0
    #   error(*8): 0
