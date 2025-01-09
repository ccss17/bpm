"""Module for test code"""

import pathlib

import mido

import bpm


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpm.bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(midi_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpm.bpm_estimator_pretty_midi(midi_path)))


def test_get_bpm_from_midi(midi_path):
    """Test get_bpm_from_midi"""
    print(round(bpm.get_bpm_from_midi(midi_path)))


def test_convert_midi_format_1_to_0(midi_path, print_dominant_tempo=True):
    """test
    ref: https://stackoverflow.com/questions/55431137/
    how-to-convert-midi-type-1-files-to-midi-type-0-in-python-or-command-line"""
    mid = mido.MidiFile(midi_path)
    merged_track = mido.merge_tracks(mid.tracks)
    print(f"\nTrack 0: {merged_track.name}\n")
    bpm.print_track(merged_track, mid, print_dominant_tempo=print_dominant_tempo)


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
    # analysis_midi(samples[3]["mid"], print_dominant_tempo=True, convert_1_to_0=True)
    # test_get_bpm_from_midi(samples[3]["mid"])

    # test_convert_midi_format_1_to_0(samples[2]["mid"])
    # data_path = pathlib.Path("dataset/가창자_s02")
    # for i, mid_path in enumerate(data_path.rglob("*.mid")):
    #     if i == 4:
    #         # test_convert_midi_format_1_to_0(mid_path, print_dominant_tempo=False)
    #         test_convert_midi_format_1_to_0(mid_path, print_dominant_tempo=True)

    # data_path = pathlib.Path("d:/dataset/004.다화자 가창 데이터")
    # data_path = pathlib.Path("d:/dataset/177.다음색 가이드보컬 데이터")
    data_path = pathlib.Path("dataset/SINGER_16")
    bpm.statistics_estimated_bpm_error(data_path)
    data_path = pathlib.Path("dataset/가창자_s02")
    bpm.statistics_estimated_bpm_error(data_path)
