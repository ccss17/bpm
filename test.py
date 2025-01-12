"""Module for test code"""

import pathlib

import bpmlib

import mido


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
    bpmlib.print_track(
        merged_track, mid.ticks_per_beat, blind_note_lyrics=blind_note_lyrics
    )


def test_create_sample_midi1(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=127, time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.Message("note_on", note=74, velocity=127, time=4))
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


def test_create_sample_midi5(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 2
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="a", time=10))
    track.append(mido.MetaMessage("lyrics", text="b", time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="c", time=10))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="d", time=10))
    track.append(mido.Message("note_on", note=64, velocity=64, time=4))
    track.append(mido.MetaMessage("lyrics", text="e", time=10))
    track.append(mido.Message("note_off", note=64, velocity=127, time=8))
    track.append(mido.MetaMessage("lyrics", text="f", time=10))

    mid.save(midi_path)


def test_create_sample_midi6(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 1
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=61, velocity=64, time=1))
    track.append(mido.Message("note_off", note=61, velocity=127, time=1))

    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="a", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="b", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="c", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="d", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="e", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="f", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))

    mid.save(midi_path)


def test_create_sample_midi7(midi_path):
    """test_sample_midi"""
    mid = mido.MidiFile()
    mid.ticks_per_beat = 1
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60), time=0))
    track.append(mido.Message("note_on", note=61, velocity=64, time=0))
    track.append(mido.Message("note_off", note=61, velocity=127, time=1))

    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1a", time=0))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1b", time=1))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1c", time=2))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1d", time=3))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1e", time=4))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))
    track.append(mido.Message("note_on", note=62, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="1f", time=5))
    track.append(mido.Message("note_off", note=62, velocity=127, time=1))

    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2a", time=0))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2b", time=1))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2c", time=2))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2d", time=3))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2e", time=4))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))
    track.append(mido.Message("note_on", note=63, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="2f", time=5))
    track.append(mido.Message("note_off", note=63, velocity=127, time=2))

    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3a", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=1))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3b", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=2))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3c", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=3))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3d", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=4))
    track.append(mido.Message("note_on", note=64, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="3e", time=0))
    track.append(mido.Message("note_off", note=64, velocity=127, time=5))

    track.append(mido.Message("note_on", note=65, velocity=66, time=0))
    track.append(mido.MetaMessage("lyrics", text="4a", time=0))
    track.append(mido.MetaMessage("lyrics", text="4b", time=0))
    track.append(mido.Message("note_off", note=65, velocity=127, time=1))
    track.append(mido.Message("note_on", note=65, velocity=66, time=1))
    track.append(mido.MetaMessage("lyrics", text="4c", time=0))
    track.append(mido.MetaMessage("lyrics", text="4d", time=1))
    track.append(mido.Message("note_off", note=65, velocity=127, time=2))
    track.append(mido.Message("note_on", note=65, velocity=66, time=2))
    track.append(mido.MetaMessage("lyrics", text="4e", time=1))
    track.append(mido.MetaMessage("lyrics", text="4f", time=0))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))
    track.append(mido.Message("note_on", note=65, velocity=66, time=3))
    track.append(mido.MetaMessage("lyrics", text="4g", time=1))
    track.append(mido.MetaMessage("lyrics", text="4h", time=1))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))
    track.append(mido.Message("note_on", note=65, velocity=66, time=4))
    track.append(mido.MetaMessage("lyrics", text="4i", time=1))
    track.append(mido.MetaMessage("lyrics", text="4j", time=2))
    track.append(mido.Message("note_off", note=65, velocity=127, time=3))

    track.append(mido.Message("note_on", note=66, velocity=66, time=0))
    track.append(mido.Message("note_off", note=66, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="5a", time=0))
    track.append(mido.Message("note_on", note=67, velocity=66, time=0))
    track.append(mido.Message("note_off", note=67, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="5b", time=0))
    track.append(mido.Message("note_on", note=68, velocity=66, time=0))
    track.append(mido.Message("note_off", note=68, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="5c", time=1))
    track.append(mido.Message("note_on", note=69, velocity=66, time=0))
    track.append(mido.Message("note_off", note=69, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="5d", time=1))
    track.append(mido.Message("note_on", note=70, velocity=66, time=0))
    track.append(mido.Message("note_off", note=70, velocity=127, time=1))
    track.append(mido.MetaMessage("lyrics", text="5e", time=2))
    track.append(mido.Message("note_on", note=71, velocity=66, time=0))
    track.append(mido.Message("note_off", note=71, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="5f", time=2))
    track.append(mido.Message("note_on", note=72, velocity=66, time=0))
    track.append(mido.Message("note_off", note=72, velocity=127, time=2))
    track.append(mido.MetaMessage("lyrics", text="5g", time=2))
    track.append(mido.Message("note_on", note=73, velocity=66, time=1))
    track.append(mido.Message("note_off", note=73, velocity=127, time=2))

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
    # test_get_bpm_from_midi(samples[0]["mid"])

    # for sample in samples:
    #     print(
    #         f'{bpmlib.bpm_estimator_librosa(sample["wav"])[0]:.2f}'
    #         + f' {bpmlib.get_bpm_from_midi(sample["mid"]):.2f}'
    #     )

    #
    # ANALYSIS MIDI FILE
    #
    # bpmlib.analysis_midi_file(samples[0]["mid"], print_bound_per_track=55)
    # bpmlib.analysis_midi_file(samples[2]["mid"], print_bound_per_track=40)
    # bpmlib.analysis_midi_file(samples[3]["mid"], print_bound_per_track=20)
    # bpmlib.analysis_midi_file(samples[0]["mid"])
    # bpmlib.analysis_midi_file(samples[1]["mid"])
    # bpmlib.analysis_midi_file(samples[2]["mid"])
    # mid = bpmlib.analysis_midi_file(samples[0]["mid"])

    #
    # LYRIC PATCH TEST
    #
    # mid = bpmlib.patch_lyric(samples[0]["mid"])
    # bpmlib.analysis_midi(mid)
    # mid.save("test2.mid", unicode_encode=True)

    #
    # CONVERT MIDI FORMAT 1 TO 0
    #
    # bpmlib.analysis_midi_file(
    #     "sample/underestimated_bpm/ba_05206_+0_a_s14_f_03.mid",
    #     blind_note_lyrics=False,
    #     convert_1_to_0=True,
    # )
    # bpmlib.analysis_midi_file(samples[2]["mid"], blind_note_lyrics=True, convert_1_to_0=True)
    # bpmlib.analysis_midi_file(
    #     samples[2]["mid"], blind_note_lyrics=False, convert_1_to_0=True
    # )
    # data_path = pathlib.Path("dataset/가창자_s02")
    # for i, mid_path in enumerate(data_path.rglob("*.mid")):
    #     if i == 4:
    #         test_convert_midi_format_1_to_0(mid_path, blind_note_lyrics=True)

    #
    # CREATE SAMPLE MIDI AND ANALYSIS IT
    #
    # test_create_sample_midi1("test_sample1.mid")
    # bpmlib.analysis_midi_file("test_sample1.mid")
    # bpmlib.midi2wav("test_sample1.mid", "test_sample1.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi2("test_sample2.mid")
    # bpmlib.analysis_midi_file("test_sample2.mid")
    # bpmlib.midi2wav("test_sample2.mid", "test_sample2.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi3("test_sample3.mid")
    # bpmlib.analysis_midi_file("test_sample3.mid")
    # bpmlib.midi2wav("test_sample3.mid", "test_sample3.wav", 60)
    # print("-" * 70)
    # test_create_sample_midi4("test_sample4.mid")
    # bpmlib.analysis_midi_file("test_sample4.mid")
    # bpmlib.midi2wav("test_sample4.mid", "test_sample4.wav", 60)
    # test_create_sample_midi5("test_sample5.mid")
    # bpmlib.analysis_midi_file("test_sample5.mid")
    # bpmlib.midi2wav("test_sample5.mid", "test_sample5.wav", 60)
    # test_create_sample_midi6("test_sample6.mid")
    # bpmlib.analysis_midi_file("test_sample6.mid")
    # bpmlib.midi2wav("test_sample6.mid", "test_sample6.wav", 60)

    #
    # GET STATISTICS of ESTIMATED CORRECTED BPM ERROR
    #
    # sample_num = 1
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
    #
    # Output:
    #
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

    #
    # bpm error samples
    #
    # underestimated bpm(/2) sample:
    #   SINGER_14_10TO29_NORMAL_FEMALE_DANCE_C0555.wav
    #   [estimated bpm]=78.30, [bpm from midi file]=120.0
    # underestimated bpm(/2) sample:
    #   ba_05206_+0_a_s14_f_03.wav
    #   [estimated bpm]=95.70, [bpm from midi file]=203.98
    # overestimated bpm(*2) sample:
    #   SINGER_12_10TO29_CLEAR_FEMALE_DANCE_C0477.wav
    #   [estimated bpm]=215.33, [bpm from midi file]=120.0
    # overestimated bpm(*2) sample:
    #   ba_06573_-1_a_s09_m_03.wav
    #   [estimated bpm]=112.34, [bpm from midi file]=63.23
