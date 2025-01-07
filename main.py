"""Module for BPM estimating"""

import librosa
import pretty_midi
import mido

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


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(audio_path):
    """Function to estimate BPM from audio file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(audio_path)
    return midi_data.estimate_tempo()


def test_bpm_estimator_librosa():
    """Test bpm_estimator_librosa"""
    print(bpm_estimator_librosa(sample[0]["wav"]))


def test_bpm_estimator_pretty_midi():
    """Test bpm_estimator_pretty_midi"""
    print(bpm_estimator_pretty_midi(sample[0]["mid"]))


def test_mido():
    """Test mido
    ref: https://mido.readthedocs.io/en/stable/files/midi.html
    """
    mid = mido.MidiFile(sample[0]["mid"])
    print("type:", mid.type)
    print("ticks_per_beat:", mid.ticks_per_beat)
    print("duration:", mid.length)
    time_signature = (4, 4)
    tempo = 120
    for i, track in enumerate(mid.tracks):
        print(f"Track {i}: {track.name}")
        total_time = 0
        for j, msg in enumerate(track):
            total_time += mido.tick2second(
                msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
            )
            if j > 25:
                continue
            # print(
            #     i,
            #     j,
            #     msg,
            #     mid.ticks_per_beat,
            #     tempo,
            #     mido.tick2second(
            #         msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
            #     ),
            # )
            # if msg.is_meta:
            #     print(i, j, msg)
            # if not msg.is_meta:
            # print(msg)
            if msg.type == "lyrics":
                print(i, j, msg, msg.text, msg.text.encode("utf-8"))
            # if msg.type == "time_signature":
            #     print("*" * 20, msg.numerator, msg.denominator)
            #     time_signature = (msg.numerator, msg.denominator)
            # if msg.type == "set_tempo":
            #     tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
            #     print("*" * 20, msg.tempo, tempo)
            # if j == 8:
            #     print(
            #         "*" * 20,
            #         msg.time,
            #         mido.tick2second(
            #             msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
            #         ),
            #     )
        print("total_time", total_time)
    # mido.tempo2bpm()


if __name__ == "__main__":
    # test_bpm_estimator()
    # test_pretty_midi()
    test_mido()
