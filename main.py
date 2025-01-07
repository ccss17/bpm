"""Module for BPM estimating"""

import librosa
import pretty_midi
import mido


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(audio_path):
    """Function to estimate BPM from audio file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(audio_path)
    return midi_data.estimate_tempo()


def get_bpm_from_midi(mid_path):
    """Function to extract BPM information from midi file"""
    mid = mido.MidiFile(mid_path)
    time_signature = (4, 4)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                return mido.tempo2bpm(msg.tempo, time_signature=time_signature)
            elif msg.type == "time_signature":
                time_signature = (msg.numerator, msg.denominator)


def test_bpm_estimator_librosa(autio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpm_estimator_librosa(autio_path)[0]))


def test_bpm_estimator_pretty_midi(mid_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpm_estimator_pretty_midi(mid_path)))


def test_get_bpm_from_midi(mid_path):
    """Test get_bpm_from_midi"""
    print(round(get_bpm_from_midi(mid_path)))


# def test_mido():
#     """Test mido
#     ref: https://mido.readthedocs.io/en/stable/files/midi.html
#     """
#     mid = mido.MidiFile(sample[0]["mid"])
#     print("type:", mid.type)
#     print("ticks_per_beat:", mid.ticks_per_beat)
#     print("duration:", mid.length)
#     time_signature = (4, 4)
#     tempo = 120
#     for i, track in enumerate(mid.tracks):
#         print(f"Track {i}: {track.name}")
#         total_time = 0
#         total_time2 = 0
#         for j, msg in enumerate(track):
#             total_time += mido.tick2second(
#                 msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
#             )
#             total_time2 += msg.time
#             if j > 25:
#                 continue
#             # if msg.is_meta:
#             #     print(i, j, msg)
#             if msg.type == "lyrics":
#                 print(
#                     msg,
#                     msg.bin()[3:].decode("utf-8"),
#                 )
#             elif msg.type == "time_signature":
#                 print("*" * 20, msg.numerator, msg.denominator)
#                 time_signature = (msg.numerator, msg.denominator)
#             elif msg.type == "set_tempo":
#                 tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
#                 print("*" * 20, msg.tempo, tempo)
#             else:
#                 print(
#                     i,
#                     j,
#                     msg,
#                     mid.ticks_per_beat,
#                     tempo,
#                     mido.tick2second(
#                         msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
#                     ),
#                 )
#         print("total_time", total_time)
#         print("total_time2", total_time2)


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

    for sample in samples:
        test_bpm_estimator_librosa(sample["wav"])
        test_bpm_estimator_pretty_midi(sample["mid"])
        test_get_bpm_from_midi(sample["mid"])
        print()
    # test_mido()
