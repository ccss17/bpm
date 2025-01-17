"""Module for BPM estimating"""

import sys
import multiprocessing as mp
import random
from collections import defaultdict
import string

import numpy as np
import librosa
import pretty_midi
import mido
from mido import MidiFile
from pydub import AudioSegment
from pydub.generators import Sine

from rich import print
from rich.console import Console

DEFAULT_BPM = 120
DEFAULT_TEMPO = 500000
DEFAULT_TIME_SIGNATURE = (4, 4)


def bpm_estimator_librosa(audio_path):
    """Function to estimate BPM from audio file by librosa"""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


def bpm_estimator_pretty_midi(midi_path):
    """Function to estimate BPM from mid file by pretty_midi"""
    midi_data = pretty_midi.PrettyMIDI(midi_path)
    return midi_data.estimate_tempo()


def _bpm_from_midi_format_0(mid_obj):
    time_signature = DEFAULT_TIME_SIGNATURE  # default time signature
    for msg in mid_obj.tracks[0]:
        if msg.type == "time_signature":
            time_signature = (msg.numerator, msg.denominator)
        elif msg.type == "set_tempo":
            return mido.tempo2bpm(msg.tempo, time_signature=time_signature)


def _bpm_from_midi_format_1(mid_obj):
    bpm = DEFAULT_BPM
    time_signature = DEFAULT_TIME_SIGNATURE
    # convert midi format 1 to 0
    merged_track = mido.merge_tracks(mid_obj.tracks)
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
                tempo_mean_numerator += bpm * lyric_note_num
                total_lyric_note_num += lyric_note_num
            bpm = round(mido.tempo2bpm(msg.tempo, time_signature=time_signature))
            lyric_note_num = 0
        elif msg.type == "time_signature":
            time_signature = (msg.numerator, msg.denominator)
        elif msg.type == "end_of_track":
            tempo_mean_numerator += bpm * lyric_note_num
            total_lyric_note_num += lyric_note_num
    return tempo_mean_numerator / total_lyric_note_num


def get_bpm_from_midi(midi_path):
    """Function to extract BPM information from midi file"""
    mid = mido.MidiFile(midi_path)

    if mid.type == 0:
        return _bpm_from_midi_format_0(mid)
    elif mid.type == 1:
        return _bpm_from_midi_format_1(mid)
    elif mid.type == 2:
        raise NotImplementedError
    else:
        raise NotImplementedError


def patch_lyric(
    midi_path,
    out_path,
    src_encode="cp949",
    tgt_encode="utf-8",
):
    """Function to patch lyric encoding"""
    mid = mido.MidiFile(midi_path)
    for track in mid.tracks:
        for msg in track:
            if msg.type == "lyrics":
                msg.text = (
                    msg.bin()[3:]
                    .decode(src_encode)
                    .encode(tgt_encode)
                    .decode(tgt_encode)
                )
    mid.save(
        out_path,
        unicode_encode=True,
    )


class MidiAnalyser:
    """Class for analysis midi file"""

    def __init__(
        self,
        midi_path,
    ):
        sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
        self.midi_path = midi_path
        self.mid = mido.MidiFile(midi_path)
        self.ticks_per_beat = self.mid.ticks_per_beat
        self.type = self.mid.type

    def analysis(
        self,
        convert_1_to_0=False,
        print_bound_per_track=float("inf"),
        blind_note_lyrics=False,
    ):
        """method to analysis"""
        self.print_bound_per_track = print_bound_per_track
        self.blind_note_lyrics = blind_note_lyrics
        self.convert_1_to_0 = convert_1_to_0

        # meta information of midi file
        print(f"ANALYSIS MIDI FILE: {self.midi_path}")
        print("[MIDI File Header]")
        print("mid file type:", self.mid.type)
        print("ticks per beat:", self.mid.ticks_per_beat)
        print("total duration:", self.mid.length)

        if self.mid.type == 1 and self.convert_1_to_0:
            self.mid.tracks = [mido.merge_tracks(self.mid.tracks)]

        for i, track in enumerate(self.mid.tracks):
            print(f"\nTrack {i}: {track.name}\n")
            MidiTrackAnalyser(self, track).analysis()


class MidiTrackAnalyser:
    """Class for analysis midi track"""

    def __init__(self, mid_analyser, track):
        self.mid_analyser = mid_analyser
        self.track = track

        # default setting
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.bpm = DEFAULT_BPM
        self.tempo = DEFAULT_TEMPO
        self.lyric_encode = "utf-8"

        self.time = 0
        self.total_time = 0
        self.lyric_note_num = 0
        self.first_tempo = True
        self.color_list = [15, 165, 47, 9, 87, 121, 27, 190]
        self.note_queue = {}
        self.idx_info = ""

    def analysis(self):
        for i, msg in enumerate(self.track):
            self.idx_info = f"[color(244)]{i:4}[/color(244)]"
            if i > self.mid_analyser.print_bound_per_track:
                break
            self.time = mido.tick2second(
                msg.time,
                ticks_per_beat=self.mid_analyser.ticks_per_beat,
                tempo=self.tempo,
            )
            self.total_time += self.time
            if msg.type == "note_on":
                self.lyric_note_num += 1
                if not self.mid_analyser.blind_note_lyrics:
                    note_address = self.note_queue_empty_address()
                    self.note_queue[note_address] = msg.note
                    self.printing(
                        self.idx_info,
                        f"{self.note_on_info(msg.note, color=f'color({self.color_list[note_address]})')}",
                        self.time_info(msg.time),
                        f"[color(240)](note={msg.note})[/color(240)]",
                    )
            elif msg.type == "note_off":
                self.lyric_note_num += 1
                if not self.mid_analyser.blind_note_lyrics:
                    note_idx = self.note_queue_value_address(msg.note)
                    self.printing(
                        self.idx_info,
                        f"{self.note_off_info(msg.note, color=f'color({self.color_list[note_idx]})')}",
                        self.time_info(msg.time),
                        f"[color(240)](note={msg.note})[/color(240)]",
                    )
                    del self.note_queue[note_idx]
            elif msg.type == "lyrics":
                self.lyric_note_num += 1
                if not self.mid_analyser.blind_note_lyrics:
                    try:
                        msg.bin()[3:].decode(self.lyric_encode)
                    except UnicodeDecodeError:
                        self.lyric_encode = "cp949"
                    if not self.note_queue and (
                        self.track[i + 1].type != "note_on"
                        or self.track[i + 1].time != 0
                    ):  # error case
                        lyric_style = "white on red"
                        border_color = "white on red"
                    else:
                        lyric_style = "bold #98ff29"
                        border_color = f"color({self.color_list[note_address]})"
                    self.print_lyric(
                        msg,
                        lyric_style=lyric_style,
                        border_color=border_color,
                    )
            elif msg.type == "set_tempo":
                if not self.first_tempo and self.mid_analyser.convert_1_to_0:
                    self.print_lyric_note_num()
                else:
                    self.first_tempo = False
                self.tempo = msg.tempo
                self.bpm = round(
                    mido.tempo2bpm(msg.tempo, time_signature=self.time_signature)
                )
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Tempo]"),
                    f"[white]BPM=[/white][color(190)]{self.bpm}[/color(190)]",
                    self.time_info(msg.time),
                    f"[color(240)]Tempo={msg.tempo}[/color(240)]",
                )
                self.lyric_note_num = 0
            elif msg.type == "end_of_track":
                if self.mid_analyser.convert_1_to_0:
                    self.print_lyric_note_num()
                self.printing(
                    self.idx_info,
                    self.msg_type_info(
                        "[End of Track]",
                    ),
                    self.time_info(msg.time),
                )
            elif msg.type == "channel_prefix":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Channel Prefix]"),
                    f"[color(240)]channel={msg.channel}[/color(240)]",
                    self.time_info(msg.time),
                )
            elif msg.type == "track_name":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Track name]"),
                    f"{msg.bin()[3:].decode(self.lyric_encode)}",
                    self.time_info(msg.time),
                )
            elif msg.type == "instrument_name":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Instrument Name]"),
                    f"[color(240)]{msg.name}[/color(240)]",
                    self.time_info(msg.time),
                )
            elif msg.type == "smpte_offset":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[SMPTE]"),
                    f"[color(240)]{msg}[/color(240)]",
                    self.time_info(msg.time),
                )
            elif msg.type == "key_signature":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Key Signature]"),
                    f"{msg.key}",
                    self.time_info(msg.time),
                )
            elif msg.type == "time_signature":
                self.printing(
                    self.idx_info,
                    self.msg_type_info("[Time Signature]"),
                    f"{msg.numerator}/{msg.denominator}",
                    self.time_info(msg.time),
                    f"[color(240)](clocks_per_click={msg.clocks_per_click},",
                    f"notated_32nd_notes_per_beat={msg.notated_32nd_notes_per_beat},[/color(240)]",
                )
                self.time_signature = (msg.numerator, msg.denominator)
            else:
                print(self.idx_info, msg)

        if self.mid_analyser.print_bound_per_track == float("inf"):
            print("total time", self.total_time)
            print("lyric encode:", self.lyric_encode)

    @staticmethod
    def printing(*strings):
        print(" ".join([*strings]))

    def time_info(self, ticks):
        if ticks == 0:
            main_color = sub_color = "color(240)"
        else:
            main_color = "#ffffff"
            sub_color = "white"
        return " ".join(
            [
                f"[{main_color}]{self.time:4.2f}[/{main_color}][{sub_color}]/{self.total_time:6.2f}[/{sub_color}]",
                f"[{sub_color}]time=[/{sub_color}][{main_color}]{ticks:<3}[/{main_color}]",
                f"",
            ]
        )

    def msg_type_info(self, msg_type):
        return f"[black on white]{msg_type}[/black on white]"

    def print_lyric_note_num(self):
        color = "color(240)" if self.lyric_note_num == 0 else "color(47)"
        Console(width=55).rule(
            f"[bold {color}]Total item num of BPM({self.bpm}): {self.lyric_note_num}",
            style=f"{color}",
        )

    def print_lyric(
        self,
        msg,
        lyric_style="bold #98ff29",
        border_color="white",
    ):
        lyric = msg.bin()[3:].decode(self.lyric_encode).strip()
        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = (
            f"{lyric:^5}"
            if lyric in string.ascii_letters + string.digits
            else f"{lyric:^4}"
        )
        self.printing(
            self.idx_info,
            border + f"[{lyric_style}]" + lyric_info + f"[/{lyric_style}]" + border,
            self.time_info(msg.time),
        )

    def note_info(self, note):
        return f"{pretty_midi.note_number_to_name(note):^5}"

    def note_on_info(self, note, color="white"):
        return f"[{color}]┌{self.note_info(note)}┐[/{color}]"

    def note_off_info(self, note, color="white"):
        return f"[{color}]└{self.note_info(note)}┘[/{color}]"

    def note_queue_empty_address(self):
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def note_queue_value_address(self, value):
        for k, v in self.note_queue.items():
            if v == value:
                return k


def estimated_bpm_error(audio_path, midi_path):
    """Function to calculate error of estimated bpm"""
    assert midi_path.name.split(".")[0] == audio_path.name.split(".")[0]
    estimated_bpm = bpm_estimator_librosa(audio_path)[0]
    bpm_from_midi_file = get_bpm_from_midi(midi_path)

    error = abs(estimated_bpm - bpm_from_midi_file)
    corrected_overestimated_bpm_error_8 = abs(estimated_bpm / 8 - bpm_from_midi_file)
    corrected_overestimated_bpm_error_4 = abs(estimated_bpm / 4 - bpm_from_midi_file)
    corrected_overestimated_bpm_error_2 = abs(estimated_bpm / 2 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_2 = abs(estimated_bpm * 2 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_4 = abs(estimated_bpm * 4 - bpm_from_midi_file)
    corrected_underestimated_bpm_error_8 = abs(estimated_bpm * 8 - bpm_from_midi_file)

    selected_error = np.argmin(
        [
            corrected_overestimated_bpm_error_8,
            corrected_overestimated_bpm_error_4,
            corrected_overestimated_bpm_error_2,
            error,
            corrected_underestimated_bpm_error_2,
            corrected_underestimated_bpm_error_4,
            corrected_underestimated_bpm_error_8,
        ]
    )

    corrected_error_2 = min(
        error, corrected_overestimated_bpm_error_2, corrected_underestimated_bpm_error_2
    )
    corrected_error_4 = min(
        corrected_error_2,
        corrected_overestimated_bpm_error_4,
        corrected_underestimated_bpm_error_4,
    )
    corrected_error_8 = min(
        corrected_error_4,
        corrected_overestimated_bpm_error_8,
        corrected_underestimated_bpm_error_8,
    )
    return (
        error,
        corrected_error_2,
        corrected_error_4,
        corrected_error_8,
        selected_error,
    )


def statistics_estimated_bpm_error(path_obj, sample_num=None):
    """Function to get statistics of errors of estimated bpm
    by multiprocessing"""

    with mp.Pool(mp.cpu_count()) as p:
        samples = zip(sorted(path_obj.rglob("*.wav")), sorted(path_obj.rglob("*.mid")))
        if sample_num:
            samples = list(samples)
            if sample_num < len(samples):
                samples = random.sample(samples, k=sample_num)
        error_array = np.array(p.starmap(estimated_bpm_error, samples))

    print(
        f"error(0); mean/std: {np.mean(error_array[:, 0]):5.2f}, {np.std(error_array[:, 0]):5.2f}"
    )
    print(
        f"error(2); mean/std: {np.mean(error_array[:, 1]):5.2f}, {np.std(error_array[:, 1]):5.2f}"
    )
    print(
        f"error(4); mean/std: {np.mean(error_array[:, 2]):5.2f}, {np.std(error_array[:, 2]):5.2f}"
    )
    print(
        f"error(8); mean/std: {np.mean(error_array[:, 3]):5.2f}, {np.std(error_array[:, 3]):5.2f}"
    )

    selected_error_frequencies = np.bincount(error_array[:, 4].astype(np.int64))
    selected_error_frequencies = np.pad(
        selected_error_frequencies,
        (0, 7 - selected_error_frequencies.shape[0]),
        "constant",
        constant_values=(0, 0),
    )
    print("selected error:")
    print(f"  error(/8): {selected_error_frequencies[0]}")
    print(f"  error(/4): {selected_error_frequencies[1]}")
    print(f"  error(/2): {selected_error_frequencies[2]}")
    print(f"  error(0) : {selected_error_frequencies[3]}")
    print(f"  error(*2): {selected_error_frequencies[4]}")
    print(f"  error(*4): {selected_error_frequencies[5]}")
    print(f"  error(*8): {selected_error_frequencies[6]}")


def midi2wav(midi_path, wav_path, bpm):
    """Function to convert midi to wav
    ref: https://gist.github.com/jiaaro/339df443b005e12d6c2a"""

    def note_to_freq(note, concert_A=440.0):
        """
        from wikipedia: http://en.wikipedia.org/wiki/MIDI_Tuning_Standard#Frequency_values
        """
        return (2.0 ** ((note - 69) / 12.0)) * concert_A

    mid = MidiFile(midi_path)
    output = AudioSegment.silent(mid.length * 1000.0)

    def ticks_to_ms(ticks):
        tick_ms = (60000.0 / bpm) / mid.ticks_per_beat
        return ticks * tick_ms

    for track in mid.tracks:
        # position of rendering in ms
        current_pos = 0.0
        current_notes = defaultdict(dict)

        for msg in track:
            current_pos += ticks_to_ms(msg.time)
            if msg.type == "note_on":
                current_notes[msg.channel][msg.note] = (current_pos, msg)
            if msg.type == "note_off":
                start_pos, start_msg = current_notes[msg.channel].pop(msg.note)
                duration = current_pos - start_pos
                signal_generator = Sine(note_to_freq(msg.note))
                rendered = (
                    signal_generator.to_audio_segment(
                        duration=duration - 50, volume=-20
                    )
                    .fade_out(100)
                    .fade_in(30)
                )
                output = output.overlay(rendered, start_pos)
    output.export(wav_path, format="wav")
