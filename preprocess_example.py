import pretty_midi
import mido
import torchaudio
from torchaudio.transforms import Resample

import numpy as np
import librosa


def resample(wav_path, target_sr, normalize=False):
    MAX_WAV_VALUE = 32768.0
    wav, source_sr = torchaudio.load(wav_path, normalize=False)
    wav = wav / MAX_WAV_VALUE
    wav = Resample(source_sr, target_sr, dtype=wav.dtype)(wav)
    if not normalize:
        wav = (wav * MAX_WAV_VALUE).clamp(-MAX_WAV_VALUE, MAX_WAV_VALUE - 1)
    return wav


def get_tempo_from_midi(midi_path):
    def estimate_tempo_from_midi(midi_path):
        md = pretty_midi.PrettyMIDI(midi_path)
        return md.estimate_tempo()

    md = mido.MidiFile(midi_path)
    tempo = None
    for msg in md:
        if msg.type == "set_tempo":
            tempo = mido.tempo2bpm(msg.tempo)
    if tempo is None:
        tempo = estimate_tempo_from_midi(midi_path)
    return tempo


def trim_head_tail_silence(
    audio_path, sr, db_threshold=-40, win_l=300, win_s=20
):
    """
    주어진 오디오에서 non-silence 구간의 시작과 끝 시간을 반환

    Args:
        audio (np.ndarray): 입력 오디오 신호 (1D array).
        sr (int): 오디오 샘플링 레이트.
        db_threshold (float): 음소거로 간주할 소리 크기 (dB).
        win_l (int): 긴 윈도우 길이 (ms).
        win_s (int): 짧은 윈도우 길이 (ms).

    Returns:
        tuple: (non_silence_start, non_silence_end) in seconds.
    """

    wav = resample(audio_path, sr)
    audio, _ = librosa.load(
        audio_path, sr=sr, mono=False
    )  # Load an audio file with librosa.

    # 모노 변환
    if len(audio.shape) > 1:
        audio = librosa.to_mono(audio)

    # 절대 진폭 계산
    abs_amp = np.abs(audio - np.mean(audio))

    # 긴 윈도우 로컬 최대값 계산
    win_ln = round(sr * win_l / 1000)
    win_sn = round(sr * win_s / 1000)
    step = win_ln // 2
    win_max_db = librosa.amplitude_to_db(
        np.maximum.reduceat(abs_amp, range(0, len(abs_amp), step))[
            : len(abs_amp) // step
        ]
    )

    # 음소거 구간 탐지
    silence = win_max_db < db_threshold
    non_silence_indices = np.where(~silence)[0]

    if non_silence_indices.size == 0:
        return (None, None)  # Non-silence 구간이 없음

    # 처음과 마지막 non-silence 구간
    first_non_silence = non_silence_indices[0] * step
    last_non_silence = (non_silence_indices[-1] + 1) * step

    # 샘플에서 시간으로 변환
    start_time = first_non_silence / sr
    end_time = min(len(audio), last_non_silence) / sr

    silence_removed_wav = wav[0][int(start_time * sr) : int(end_time * sr)]
    silence_removed_wav = np.array(silence_removed_wav)

    return silence_removed_wav, start_time, end_time


def load_note_pitch_duration_from_midi(midi_path, start=None, end=None):
    md = pretty_midi.PrettyMIDI(midi_path)
    md.remove_invalid_notes()
    notes = md.instruments[0].notes

    note_pitch = []
    note_duration = []
    filtered_notes = []

    # 앞뒤 silence 에 속한 노트들 제거
    if start is not None and end is not None:
        for note in notes:
            # 노트가 non-silence 영역 이전에 끝나는 경우: 제외
            if note.end < start:
                continue
            # 노트가 non-silence 영역 이후에 시작하는 경우: 제외
            elif note.start > end:
                continue
            else:
                # 노트의 시작과 끝을 non-silence 영역에 맞게 조정
                if note.start < start:
                    note.start = start
                if note.end > end:
                    note.end = end
                # 노트의 길이가 최소 길이 이상인지 확인
                if note.end - note.start >= 0.1:
                    filtered_notes.append(note)
        # 원본 노트 리스트를 필터링된 노트 리스트로 교체
        notes = filtered_notes

    for i in range(len(notes) - 1):
        error = notes[i + 1].start - notes[i].end
        if error < 0 or (error > 0 and error < 0.3):
            notes[i].end = notes[i + 1].start

        note_duration.append(notes[i].end - notes[i].start)
        note_pitch.append(notes[i].pitch)
        if error > 0.3:
            note_duration.append(error)
            note_pitch.append(0)

    note_duration.append(
        notes[len(notes) - 1].end - notes[len(notes) - 1].start
    )
    note_pitch.append(notes[len(notes) - 1].pitch)

    return np.array(note_pitch), np.array(note_duration)


def duration_secs_to_frames(note_duration_sec, sr, hop_length):
    """
    If the unit of the note duration is "seconds", the unit should be converted to "frames"
    Furthermore, it should be rounded to integer and this causes rounding error
    This function includes error handling process that alleviates the rounding error
    """

    frames_per_sec = sr / hop_length
    note_duration_frame = note_duration_sec * frames_per_sec
    note_duration_frame_int = note_duration_frame.copy().astype(np.int64)
    errors = (
        note_duration_frame - note_duration_frame_int
    )  # rounding error per each note
    errors_sum = int(np.sum(errors))

    top_k_errors_idx = errors.argsort()[-errors_sum:][::-1]

    for i in top_k_errors_idx:
        note_duration_frame_int[i] += 1

    return note_duration_frame_int


# hyperparameters
sampling_rate = 22050
hop_length = 256
frame_per_sec = sampling_rate / hop_length

# wav 파일의 앞,뒤 침묵 (silence) 제거
wav_path = "/home/sjkim/dataset/bertapc_v2/bak/gv/data/wav_22050/SINGER_92_OVER49_NORMAL_FEMALE_BALLAD_C3973.wav"  # 22.05k wav 파일 경로 입력
silence_removed_wav, start_sec, end_sec = trim_head_tail_silence(
    wav_path, sampling_rate, db_threshold=-40, win_l=300, win_s=20
)

# 미디 파일 로드 및 note pitch, note duration 추출
midi_path = "/home/sjkim/dataset/bertapc_v2/bak/gv/data/midi/SINGER_92_OVER49_NORMAL_FEMALE_BALLAD_C3973.mid"
note_pitch, note_duration_sec = load_note_pitch_duration_from_midi(
    midi_path, start=start_sec, end=end_sec
)

# bpm 을 기반으로 note_duration_sec 을 quantize (quantize 최소 단위: 32분 음표)
bpm = get_tempo_from_midi(midi_path)
quarter_note_duration = 60 / bpm
thirty_second_note_duration = quarter_note_duration / 8
quantization_step = thirty_second_note_duration
# [TODO] quantize_note_duration 함수 작성
## 입력:
## - note_duration_sec : numpy.FloatArray, quantization_step : float
## 출력 :
## - quantized_note_duration_sec (32 분 음표 단위로 quantize 된 note duration) : numpy.FloatArray
quantized_note_duration_sec = quantize_note_duration(
    note_duration_sec, quantization_step
)

# rounding (단위 변환: secs -> # of frames) 및 rounding error 교정
note_duration_frame = duration_secs_to_frames(
    quantized_note_duration_sec, sampling_rate, hop_length
)
