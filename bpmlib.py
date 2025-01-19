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

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

import note

DEFAULT_BPM = 120
DEFAULT_TEMPO = 500000
DEFAULT_TIME_SIGNATURE = (4, 4)


def pretty_note_info(note_info):
    """pretty_note_info(note_info)"""
    beat = float(note_info[0])
    if 4 / beat <= 1:
        note_name = f"{1/(4/beat)}온음표"
        # return f"{note_info[-1]:3} {beat:<6.3} {1/(4/beat):<6}온음표 {note_info[2]}"
        # return note_info[-1], f"{beat}박", f"{1/(4/beat)}온음표", note_info[2]
    else:
        note_name = f"{4/beat:.4}분음표"
        # return f"{note_info[-1]:3} {beat:<6.3} {4/beat:<6.5}분음표 {note_info[2]}"
        # return note_info[-1], f"{beat}박", f"{4/beat:.5}분음표", note_info[2]
    return note_info[-1], f"{beat:.3}박", note_name, note_info[2]


def show_notes():
    """Function to show pre-defined notes"""
    for k, v in note.NOTE.items():
        rprint(*pretty_note_info((k, *v)))


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


class MidiAnalyzer:
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
        self.print_bound_per_track = None
        self.blind_note_lyrics = None
        self.convert_1_to_0 = None
        self.blind_time = None

    def analysis(
        self,
        convert_1_to_0=False,
        print_bound_per_track=float("inf"),
        blind_note_lyrics=False,
        blind_time=False,
        target_track_list=None,
    ):
        """method to analysis"""
        self.print_bound_per_track = print_bound_per_track
        self.blind_note_lyrics = blind_note_lyrics
        self.convert_1_to_0 = convert_1_to_0
        self.blind_time = blind_time

        # meta information of midi file
        header_style = "#100e23 on #91ddff blink"
        header_style = "black on white blink"

        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.mid.type}",
                f"ticks per beat: {self.mid.ticks_per_beat}",
                f"total duration: {self.mid.length}[/{header_style}]",
            ]
        )

        rprint(
            Panel(
                header_info,
                title=f"{self.mid.filename}",
                subtitle="[MIDI File Header]",
                style=f"{header_style}",
                border_style=f"{header_style}",
            )
        )

        if self.mid.type == 1 and self.convert_1_to_0:
            self.mid.tracks = [mido.merge_tracks(self.mid.tracks)]

        quantization_error, quantization_mean = 0, 0
        for i, track in enumerate(self.mid.tracks):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if target_track_list is None or track.name in target_track_list:
                mta = MidiTrackAnalyzer(self, track)
                _quantization_error, _quantization_mean = mta.analysis()
                quantization_error += _quantization_error
                quantization_mean += _quantization_mean

        if target_track_list is None or target_track_list:
            if target_track_list is None:
                mean_denominator = len(self.mid.tracks)
            else:
                mean_denominator = len(target_track_list)
            total_quantization_mean = quantization_mean / mean_denominator
            print()
            rprint(
                "Total quantization error/mean of track error mean: "
                + f"{float(quantization_error):.5}/{total_quantization_mean:.5}"
            )


class MidiTrackAnalyzer:
    """Class for analysis midi track"""

    def __init__(self, mid_analyzer, track):
        self.mid_analyzer = mid_analyzer
        self.track = track

        # default setting
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.bpm = DEFAULT_BPM
        self.tempo = DEFAULT_TEMPO
        self.text_encode = "utf-8"

        self.time = 0
        self.ticks = 0
        self.total_time = 0
        self.lyric_note_num = 0
        self.quantization_error = 0
        self.quantization_num = 0
        self.first_tempo = True
        self.note_queue = {}
        self.idx_info = ""
        self.msg = None

    def analysis(self):
        """analysis"""
        note_address = 0
        lyric = ""
        for i, msg in enumerate(self.track):
            self.idx_info = f"[color(244)]{i:4}[/color(244)]"
            if i > self.mid_analyzer.print_bound_per_track:
                break
            self.ticks = msg.time
            self.msg = msg
            self.time = mido.tick2second(
                self.ticks,
                ticks_per_beat=self.mid_analyzer.ticks_per_beat,
                tempo=self.tempo,
            )
            self.total_time += self.time
            if msg.type == "note_on":
                note_address = self._analysis_note_on(msg)
            elif msg.type == "note_off":
                self._analysis_note_off(msg)
            elif msg.type == "lyrics":
                lyric += self._analysis_lyric(msg, i, note_address)
                # lyric = msg.bin()[3:].decode("cp949").encode("utf-8").decode("utf-8")
                # msg.text = f"{lyric}{i}"
            elif msg.type == "text":
                self._analysis_text(msg)
            elif msg.type == "set_tempo":
                self._analysis_set_tempo(msg)
            elif msg.type == "end_of_track":
                self._analysis_end_of_track(msg)
            elif msg.type == "channel_prefix":
                self._analysis_channel_prefix(msg)
            elif msg.type == "track_name":
                self._analysis_track_name(msg)
            elif msg.type == "instrument_name":
                self._analysis_instrument_name(msg)
            elif msg.type == "smpte_offset":
                self._analysis_smpte_offset(msg)
            elif msg.type == "key_signature":
                self._analysis_key_signature(msg)
            elif msg.type == "time_signature":
                self._analysis_time_signature(msg)
            else:
                self._printing(
                    self.idx_info,
                    self._msg_type_info(f"\[{msg.type}]"),
                    f"{msg}",
                    self._time_info(msg.time)
                    if not self.mid_analyzer.blind_time
                    else "",
                )

        quantization_error_mean = 0
        if self.mid_analyzer.print_bound_per_track == float("inf"):
            rprint(f"Track lyric encode: {self.text_encode}")
            rprint(f"Track total time: {self.total_time}")
            if self.quantization_num != 0:
                quantization_error_mean = (
                    self.quantization_error / self.quantization_num
                )
                rprint(
                    "Track total quantization error/mean: "
                    + f"{self.quantization_error:.5}/{quantization_error_mean:.5}"
                )
        print(f'LYRIC: "{lyric}"')
        return self.quantization_error, quantization_error_mean

    def _quantization_round_up(self):
        """select upper bound"""
        if self.ticks == 0:
            return None, None
        beat = self.ticks / self.mid_analyzer.ticks_per_beat
        quantized_info = error = None
        for i, (predefined_beat, values) in enumerate(note.NOTE.items()):
            error = abs(beat - predefined_beat)
            if i == 0:
                if beat > predefined_beat:
                    quantized_info = predefined_beat, *values
                    break
            else:
                prev_predefined_beat = list(note.NOTE.keys())[i - 1]
                if beat > predefined_beat and beat < prev_predefined_beat:
                    quantized_info = predefined_beat, *note.NOTE[prev_predefined_beat]
                    break
        else:
            quantized_info = predefined_beat, *values
        return error, quantized_info

    def _quantization_min(self, beat):
        """select minimum error"""
        min_error = float("inf")
        min_error_abs = None
        min_error_info = None
        if self.ticks == 0:
            return None, None, None
        for predefined_beat, values in note.NOTE.items():
            error = predefined_beat - beat
            error_abs = abs(error)
            if error_abs < min_error:
                min_error = error
                min_error_abs = error_abs
                min_error_info = predefined_beat, *values
        return min_error, min_error_abs, min_error_info

    def _quantization_info(self, quantization_color="color(85)"):
        """quantization_info"""
        beat = self.ticks / self.mid_analyzer.ticks_per_beat
        error, error_abs, error_info = self._quantization_min(beat)
        # error, error_info = self._quantization_round_up()
        if error != None:
            note_symbol, beat_msg, beat_note_name, note_name = pretty_note_info(
                error_info
            )
            self.quantization_error += error_abs
            self.quantization_num += 1
            error = round(error, 3)
            return (
                f"[{quantization_color}]"
                + f"{note_symbol:2}{note_name}"
                + f"[/{quantization_color}]"
                + f"[color(249)]({beat_msg};{beat_note_name})[/color(249)]"
                + " "
                + f"[color(245)]{error}[/color(245)]"
                + f"[color(240)]({float(error_info[0]):.3}-{float(beat):.3})[/color(240)]"
            )
        else:
            return ""

    def _analysis_note_on(self, msg):
        self.lyric_note_num += 1
        if not self.mid_analyzer.blind_note_lyrics:
            note_address = self._note_queue_empty_address()
            self.note_queue[note_address] = msg.note
            note_msg = self._note_on_info(
                msg.note,
                color=f"color({note.NOTE_COLOR_LIST[note_address % len(note.NOTE_COLOR_LIST)]})",
            )
            quantization_info = self._quantization_info()
            self._printing(
                self.idx_info,
                f"{note_msg}",
                self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
                quantization_info,
            )
            return note_address

    def _analysis_note_off(self, msg):
        self.lyric_note_num += 1
        if not self.mid_analyzer.blind_note_lyrics:
            note_idx = self._note_queue_value_address(msg.note)
            if note_idx is None:
                color = "white on red"
            else:
                color = f"color({note.NOTE_COLOR_LIST[note_idx]})"
                del self.note_queue[note_idx]
            note_msg = self._note_off_info(msg.note, color=color)
            quantization_info = self._quantization_info()
            self._printing(
                self.idx_info,
                f"{note_msg}",
                self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
                quantization_info,
            )

    def _analysis_lyric(self, msg, msg_idx, note_address):
        self.lyric_note_num += 1
        if not self.mid_analyzer.blind_note_lyrics:
            try:
                msg.bin()[3:].decode(self.text_encode)
            except UnicodeDecodeError:
                self.text_encode = "cp949"
            if not self.note_queue and (
                self.track[msg_idx + 1].type != "note_on"
                or self.track[msg_idx + 1].time != 0
            ):  # error case
                lyric_style = "white on red"
                border_color = "white on red"
            else:
                lyric_style = "bold #98ff29"
                border_color = f"color({note.NOTE_COLOR_LIST[note_address]})"
            return self._print_lyric(
                msg,
                lyric_style=lyric_style,
                border_color=border_color,
            )

    def _analysis_set_tempo(self, msg):
        if not self.first_tempo and self.mid_analyzer.convert_1_to_0:
            self._print_lyric_note_num()
        else:
            self.first_tempo = False
        self.tempo = msg.tempo
        self.bpm = round(mido.tempo2bpm(msg.tempo, time_signature=self.time_signature))
        self._printing(
            self.idx_info,
            self._msg_type_info("[Tempo]"),
            f"[white]BPM=[/white][color(190)]{self.bpm}[/color(190)]",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
            f"[color(240)]Tempo={msg.tempo}[/color(240)]",
        )
        self.lyric_note_num = 0

    def _analysis_end_of_track(self, msg):
        if self.mid_analyzer.convert_1_to_0:
            self._print_lyric_note_num()
        self._printing(
            self.idx_info,
            self._msg_type_info(
                "[End of Track]",
            ),
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_channel_prefix(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[Channel Prefix]"),
            f"[color(240)]channel={msg.channel}[/color(240)]",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_track_name(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[Track name]"),
            f"{msg.bin()[3:].decode(self.text_encode)}",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_instrument_name(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[Instrument Name]"),
            f"[color(240)]{msg.name}[/color(240)]",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_smpte_offset(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[SMPTE]"),
            f"[color(240)]{msg}[/color(240)]",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_key_signature(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[Key Signature]"),
            f"{msg.key}",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    def _analysis_time_signature(self, msg):
        self._printing(
            self.idx_info,
            self._msg_type_info("[Time Signature]"),
            f"{msg.numerator}/{msg.denominator}",
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
            f"[color(240)](clocks_per_click={msg.clocks_per_click},",
            f"notated_32nd_notes_per_beat={msg.notated_32nd_notes_per_beat},[/color(240)]",
        )
        self.time_signature = (msg.numerator, msg.denominator)

    def _analysis_text(self, msg):
        try:
            msg.bin()[3:].decode(self.text_encode)
        except UnicodeDecodeError:
            self.text_encode = "cp949"
        text = msg.bin()[3:].decode(self.text_encode).strip()
        self._printing(
            self.idx_info,
            self._msg_type_info("[Text]"),
            text,
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
        )

    @staticmethod
    def _printing(*strings):
        """print strings"""
        rprint(" ".join([s for s in strings if s]))

    def _time_info(self, ticks):
        """time_info"""
        if ticks == 0:
            main_color = sub_color = "color(238)"
        else:
            main_color = "#ffffff"
            sub_color = "white"
        info = [
            f"[{main_color}]{self.time:4.2f}[/{main_color}]"
            + f"[{sub_color}]/{self.total_time:6.2f}[/{sub_color}]",
            f"[{sub_color}]time=[/{sub_color}][{main_color}]{ticks:<3}[/{main_color}]",
        ]
        return " ".join(info)

    def _msg_type_info(self, msg_type):
        """msg_type_info"""
        return f"[black on white]{msg_type}[/black on white]"

    def _print_lyric_note_num(self):
        """_print_lyric_note_num"""
        color = "color(240)" if self.lyric_note_num == 0 else "color(47)"
        Console(width=55).rule(
            f"[bold {color}]Total item num of BPM({self.bpm}): {self.lyric_note_num}",
            style=f"{color}",
        )

    def _print_lyric(
        self,
        msg,
        lyric_style="bold #98ff29",
        border_color="white",
    ):
        """print_lyric"""

        def is_alphanum(lyric):
            for c in lyric:
                if c not in string.ascii_letters + string.digits:
                    return False
            return True

        lyric = msg.bin()[3:].decode(self.text_encode).strip()
        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = f"{lyric:^7}" if is_alphanum(lyric) else f"{lyric:^6}"
        quantization_info = self._quantization_info()
        self._printing(
            self.idx_info,
            border + f"[{lyric_style}]" + lyric_info + f"[/{lyric_style}]" + border,
            self._time_info(msg.time) if not self.mid_analyzer.blind_time else "",
            quantization_info,
        )
        return lyric

    def _note_info(self, note):
        """note_info"""
        return f"{pretty_midi.note_number_to_name(note):>3}({note})"

    def _note_on_info(self, note, color="white"):
        """note_on_info"""
        return f"[{color}]┌{self._note_info(note)}┐[/{color}]"

    def _note_off_info(self, note, color="white"):
        """note_off_info"""
        return f"[{color}]└{self._note_info(note)}┘[/{color}]"

    def _note_queue_empty_address(self):
        """_note_queue_empty_address"""
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def _note_queue_value_address(self, value):
        """_note_queue_value_address"""
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None


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

    rprint(
        f"error(0); mean/std: {np.mean(error_array[:, 0]):5.2f}, {np.std(error_array[:, 0]):5.2f}"
    )
    rprint(
        f"error(2); mean/std: {np.mean(error_array[:, 1]):5.2f}, {np.std(error_array[:, 1]):5.2f}"
    )
    rprint(
        f"error(4); mean/std: {np.mean(error_array[:, 2]):5.2f}, {np.std(error_array[:, 2]):5.2f}"
    )
    rprint(
        f"error(8); mean/std: {np.mean(error_array[:, 3]):5.2f}, {np.std(error_array[:, 3]):5.2f}"
    )

    selected_error_frequencies = np.bincount(error_array[:, 4].astype(np.int64))
    selected_error_frequencies = np.pad(
        selected_error_frequencies,
        (0, 7 - selected_error_frequencies.shape[0]),
        "constant",
        constant_values=(0, 0),
    )
    rprint("selected error:")
    rprint(f"  error(/8): {selected_error_frequencies[0]}")
    rprint(f"  error(/4): {selected_error_frequencies[1]}")
    rprint(f"  error(/2): {selected_error_frequencies[2]}")
    rprint(f"  error(0) : {selected_error_frequencies[3]}")
    rprint(f"  error(*2): {selected_error_frequencies[4]}")
    rprint(f"  error(*4): {selected_error_frequencies[5]}")
    rprint(f"  error(*8): {selected_error_frequencies[6]}")


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
