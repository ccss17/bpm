"""Module for BPM estimating"""

import librosa
import pretty_midi
from mido import MidiFile

sample = [
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


def bpm_estimator(audio_path):
    """Function to estimate BPM from audio file"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def test_bpm_estimator():
    """Test bpm_estimator"""
    print(bpm_estimator(sample[0]["wav"]))


def test_pretty_midi():
    """Test librosa"""
    midi_data = pretty_midi.PrettyMIDI(sample[0]["mid"])
    print(midi_data.estimate_tempo())


def test_mido():
    """Test mido
    ref: https://mido.readthedocs.io/en/stable/files/midi.html
    """
    mid = MidiFile(sample[2]["mid"])
    for i, track in enumerate(mid.tracks):
        print(f"Track {i}: {track.name}")
        for j, msg in enumerate(track):
            print(i, j, msg)
            # if msg.is_meta:
            #     print(i, j, msg)
            # if not msg.is_meta:
            # print(msg)
            # if msg.type == "lyrics":
            #     print(i, j, msg)
            if j == 20:
                break


if __name__ == "__main__":
    # test_bpm_estimator()
    # test_pretty_midi()
    test_mido()
