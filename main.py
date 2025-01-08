"""Module for BPM estimating"""

import librosa
import pretty_midi
import mido


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(mid_path):
    """Function to estimate BPM from mid file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(mid_path)
    return midi_data.estimate_tempo()


def get_bpm_from_midi(mid_path):
    """Function to extract BPM information from midi file"""
    mid = mido.MidiFile(mid_path)
    time_signature = (4, 4)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "time_signature":
                time_signature = (msg.numerator, msg.denominator)
            elif msg.type == "set_tempo":
                return mido.tempo2bpm(msg.tempo, time_signature=time_signature)


def test_bpm_estimator_librosa(audio_path):
    """Test bpm_estimator_librosa"""
    print(round(bpm_estimator_librosa(audio_path)[0]))


def test_bpm_estimator_pretty_midi(mid_path):
    """Test bpm_estimator_pretty_midi"""
    print(round(bpm_estimator_pretty_midi(mid_path)))


def test_get_bpm_from_midi(mid_path):
    """Test get_bpm_from_midi"""
    print(round(get_bpm_from_midi(mid_path)))


def test_mido(mid_path, lyric_encode, print_bound=float("inf")):
    """Test mido
    ref: https://mido.readthedocs.io/en/stable/files/midi.html
    """
    mid = mido.MidiFile(mid_path)
    print("[미디 파일 헤더]")
    print("mid file type:", mid.type)
    print("ticks per beat:", mid.ticks_per_beat)
    print("total duration:", mid.length)
    time_signature = (4, 4)
    tempo = 120
    for i, track in enumerate(mid.tracks):
        print()
        print(f"Track {i}: {track.name}")
        print()
        total_time = 0
        total_time2 = 0
        for j, msg in enumerate(track):
            total_time += mido.tick2second(
                msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
            )
            total_time2 += msg.time
            if j > print_bound:
                continue
            if msg.type == "note_on":
                print("┌노트 시작┐", msg)
            elif msg.type == "note_off":
                print("└노트 끝┘", msg)
            elif msg.type == "lyrics":
                print(f"  [가사] {msg.bin()[3:].decode(lyric_encode)} time={msg.time}")
            elif msg.type == "track_name":
                print("[트랙 이름]", msg)
            elif msg.type == "instrument_name":
                print(f"[악기 이름] {msg.name} time={msg.time}")
            elif msg.type == "smpte_offset":
                print(f"[SMPTE] {msg}")
            elif msg.type == "key_signature":
                print(f"[조표] {msg.key} time={msg.time}")
            elif msg.type == "time_signature":
                print(
                    f"[박자표] {msg.numerator}/{msg.denominator} 박자, "
                    + f"clocks_per_click={msg.clocks_per_click}, "
                    + f"notated_32nd_notes_per_beat={msg.notated_32nd_notes_per_beat}, "
                    + f"time={msg.time}"
                )
                time_signature = (msg.numerator, msg.denominator)
            elif msg.type == "set_tempo":
                tempo = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
                print(f"[템포] {msg.tempo}(BPM={tempo}) time={msg.time}")
            else:
                print(
                    msg,
                    mid.ticks_per_beat,
                    tempo,
                    mido.tick2second(
                        msg.time, ticks_per_beat=mid.ticks_per_beat, tempo=tempo
                    ),
                )
        print("total_time", total_time)
        print("total_time2", total_time2)


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

    # test_mido(samples[0]["mid"], lyric_encode="utf-8", print_bound=25)
    test_mido(samples[2]["mid"], lyric_encode="euc-kr", print_bound=20)
