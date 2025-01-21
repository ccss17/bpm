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

from note import Note, Rest, NOTE_COLOR_LIST

DEFAULT_BPM = 120
DEFAULT_TEMPO = 500000
DEFAULT_TIME_SIGNATURE = (4, 4)


def is_alphanum(str):
    for c in str:
        if c not in string.ascii_letters + string.digits:
            return False
    return True


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
        self.blind_note = None
        self.convert_1_to_0 = None
        self.blind_time = None

        self.track_analyzer_list = []
        for i, track in enumerate(self.mid.tracks):
            self.track_analyzer_list.append(
                MidiTrackAnalyzer(self, track, self.ticks_per_beat)
            )

    def partition(self):
        """partition"""
        for i, track_analyzer in enumerate(self.track_analyzer_list):
            track_analyzer.partition()

    def analysis(
        self,
        convert_1_to_0=False,
        print_bound_per_track=float("inf"),
        blind_note=False,
        blind_time=False,
        target_track_list=None,
    ):
        """method to analysis"""
        self.print_bound_per_track = print_bound_per_track
        self.blind_note = blind_note
        self.convert_1_to_0 = convert_1_to_0
        self.blind_time = blind_time

        # meta information of midi file
        header_style = "#100e23 on #91ddff blink"
        header_style = "black on white blink"

        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.mid.type}",
                f"ticks per beat: {self.ticks_per_beat}",
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
        # for i, track in enumerate(self.mid.tracks):
        for i, track_analyzer in enumerate(self.track_analyzer_list):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track_analyzer.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if target_track_list is None or track_analyzer.name in target_track_list:
                _quantization_error, _quantization_mean = track_analyzer.analysis(
                    convert_1_to_0=convert_1_to_0,
                    print_bound_per_track=print_bound_per_track,
                    blind_note=blind_note,
                    blind_time=blind_time,
                )
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

    def __init__(self, mid_analyzer, track, ticks_per_beat):
        self.mid_analyzer = mid_analyzer
        self.track = track
        self.name = track.name
        self.ticks_per_beat = ticks_per_beat

        self._init_values()

    def _init_values(self):
        # default setting
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.tempo = DEFAULT_TEMPO
        self.text_encode = "utf-8"

        self.total_time = 0
        self.lyric_note_num = 0
        self.quantization_error = 0
        self.quantization_num = 0
        self.first_tempo = True
        self.note_queue = {}
        self.idx_info = ""

    def get_beat(self, time):
        """get_beat"""
        return time / self.ticks_per_beat

    def partition(self):
        """partition
        박자가 4(온음표) 보다 크다 → 4보다 작아질 때 까지 4박을 독립시킨다.
        박자가 4보다 작다.
            박자가 2(2분음표)보다 크다 	→ 2박을 독립시킨다.
            박자가 1(4분음표)보다 크다 → 1박을 독립시킨다.
            박자가 0.5(8분음표)보다 크다 → 0.5박을 독립시킨다.
            박자가 0.25(16분음표)보다 크다 → 0.25박을 독립시킨다.
            박자가 0.125(32분음표)보다 크다 → 0.125박을 독립시킨다.
        박이 32분음표보다 작으면?
        """
        modified_track = []
        for i, msg in enumerate(self.track):
            modified_track.append(msg)
            if msg.type == "note_on":
                pass
            elif msg.type == "note_off":
                pass
            elif msg.type == "lyric":
                pass
        self.track = modified_track

    def analysis(
        self,
        convert_1_to_0=False,
        print_bound_per_track=float("inf"),
        blind_note=False,
        blind_time=False,
    ):
        """analysis track"""
        self._init_values()
        note_address = 0
        lyric = ""
        for i, msg in enumerate(self.track):
            if i > print_bound_per_track:
                break
            self.idx_info = f"[color(244)]{i:4}[/color(244)]"
            self.total_time += mido.tick2second(
                msg.time,
                ticks_per_beat=self.ticks_per_beat,
                tempo=self.tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ticks_per_beat": self.ticks_per_beat,
                "tempo": self.tempo,
                "idx": i,
                "total_time": self.total_time,
            }
            if msg.type == "note_on":
                self.lyric_note_num += 1
                note_address, q_error = MidiMessageAnalyzer_note_on(
                    **msg_kwarg, note_queue=self.note_queue
                ).print(blind_time=blind_time, blind_note=blind_note)
                self.quantization_error += q_error
                self.quantization_num += 1 if q_error else 0
            elif msg.type == "note_off":
                self.lyric_note_num += 1
                q_error = MidiMessageAnalyzer_note_off(
                    **msg_kwarg, note_queue=self.note_queue
                ).print(blind_time=blind_time, blind_note=blind_note)
                self.quantization_error += q_error
                self.quantization_num += 1 if q_error else 0
            elif msg.type == "lyrics":
                self.lyric_note_num += 1
                _lyric, q_error = MidiMessageAnalyzer_lyrics(
                    **msg_kwarg,
                    msg_next=self.track[i + 1],
                    note_address=note_address,
                    note_queue=self.note_queue,
                ).print(blind_time=blind_time, blind_note=blind_note)
                self.quantization_error += q_error
                self.quantization_num += 1 if q_error else 0
                lyric += _lyric
            elif msg.type == "text" or msg.type == "track_name":
                MidiMessageAnalyzer_text(
                    **msg_kwarg,
                    encoding=self.text_encode,
                ).print(blind_time=blind_time)
            elif msg.type == "set_tempo":
                if not self.first_tempo and convert_1_to_0:
                    self.print_lyric_note_num()
                self.first_tempo = False
                self.tempo = msg.tempo
                MidiMessageAnalyzer_set_tempo(
                    **msg_kwarg,
                    time_signature=self.time_signature,
                ).print(blind_time=blind_time)
            elif msg.type == "end_of_track":
                if convert_1_to_0:
                    self.print_lyric_note_num()
                MidiMessageAnalyzer_end_of_track(**msg_kwarg).print(
                    blind_time=blind_time
                )
            elif msg.type == "key_signature":
                MidiMessageAnalyzer_key_signature(**msg_kwarg).print(
                    blind_time=blind_time
                )
            elif msg.type == "time_signature":
                self.time_signature = MidiMessageAnalyzer_time_signature(
                    **msg_kwarg
                ).print(blind_time=blind_time)
            else:
                MidiMessageAnalyzer(**msg_kwarg).print(blind_time=blind_time)

        quantization_error_mean = 0
        if print_bound_per_track == float("inf"):
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

    def print_lyric_note_num(self):
        """print_lyric_note_num"""
        color = "color(240)" if self.lyric_note_num == 0 else "color(47)"
        bpm = round(mido.tempo2bpm(self.tempo, time_signature=self.time_signature))
        info = f"[bold {color}]Total item num of BPM({bpm}): {self.lyric_note_num}"
        Console(width=55).rule(info, style=f"{color}")


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


class MidiMessageAnalyzer:
    def __init__(
        self,
        msg,
        ticks_per_beat,
        tempo=DEFAULT_TEMPO,
        idx=0,
        total_time=0,
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.total_time = total_time

    def analysis(self):
        pass

    def info_type(self):
        """info_type"""
        return f"[black on white]\[{self.msg.type}][/black on white]"

    def info_time(self):
        """time_info"""
        if self.msg.time == 0:
            main_color = sub_color = "color(238)"
        else:
            main_color = "#ffffff"
            sub_color = "white"
        time_sec = mido.tick2second(
            self.msg.time,
            ticks_per_beat=self.ticks_per_beat,
            tempo=self.tempo,
        )
        return " ".join(
            [
                f"[{main_color}]{time_sec:4.2f}[/{main_color}]"
                + f"[{sub_color}]/{self.total_time:6.2f}[/{sub_color}]",
                f"[{sub_color}]time=[/{sub_color}][{main_color}]{self.msg.time:<3}[/{main_color}]",
            ]
        )

    def result(self, head="", body="", blind_time=False):
        # def analysis_result(self, head, body, body):
        """print strings"""
        time_info = "" if blind_time else self.info_time()
        # return " ".join(
        #     [self.idx_info] + [strings[0]] + time_info + [s for s in strings[1:] if s]
        # )
        _result = [self.idx_info, head, time_info, body]
        return " ".join([s for s in _result if s])

    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                body=f"[color(250)]{self.msg}[/color(250)]",
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_set_tempo(MidiMessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat,
        tempo=DEFAULT_TEMPO,
        idx=0,
        total_time=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(
            msg, ticks_per_beat, tempo=tempo, idx=idx, total_time=total_time
        )
        self.time_signature = time_signature

    def print(self, blind_time=False):
        bpm = round(mido.tempo2bpm(self.msg.tempo, time_signature=self.time_signature))
        rprint(
            self.result(
                head=self.info_type(),
                body=f"[white]BPM=[/white][color(190)]{bpm}[/color(190)]",
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_instrument_name(MidiMessageAnalyzer):
    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                body=f"[color(240)]{self.msg.name}[/color(240)]",
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_channel_prefix(MidiMessageAnalyzer):
    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                body=f"[color(240)]channel={self.msg.channel}[/color(240)]",
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_key_signature(MidiMessageAnalyzer):
    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                body=self.msg.key,
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_end_of_track(MidiMessageAnalyzer):
    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                blind_time=blind_time,
            )
        )


class MidiMessageAnalyzer_time_signature(MidiMessageAnalyzer):
    def print(self, blind_time=False):
        rprint(
            self.result(
                head=self.info_type(),
                body=f"{self.msg.numerator}/{self.msg.denominator}",
                blind_time=blind_time,
            )
        )
        return self.msg.numerator, self.msg.denominator


class MidiMessageAnalyzer_text(MidiMessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat,
        tempo=DEFAULT_TEMPO,
        idx=0,
        total_time=0,
        encoding="utf-8",
        encoding_alternative="cp949",
    ):
        super().__init__(
            msg, ticks_per_beat, tempo=tempo, idx=idx, total_time=total_time
        )
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = self.determine_encoding(encoding, encoding_alternative)

    def determine_encoding(self, *encoding_list):
        for encoding in encoding_list:
            try:
                self.encoded_text.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                return encoding
        else:
            raise UnicodeDecodeError

    def print(self, blind_time=False):
        """analysis text"""
        text = self.encoded_text.decode(self.encoding).strip()
        result = self.result(head=self.info_type(), body=text, blind_time=blind_time)
        rprint(result)


class MidiMessageAnalyzer_SoundUnit(MidiMessageAnalyzer):
    def __init__(
        self,
        msg,
        ticks_per_beat,
        tempo=DEFAULT_TEMPO,
        idx=0,
        total_time=0,
        note_queue={},
    ):
        super().__init__(
            msg,
            ticks_per_beat,
            tempo=tempo,
            idx=idx,
            total_time=total_time,
        )
        self.note_queue = note_queue

    def note_queue_empty_address(self):
        """note_queue_empty_address"""
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def get_beat(self, time):
        """get_beat"""
        return time / self.ticks_per_beat

    def quantization_min(self, time, as_rest=False):
        """select minimum error"""
        if time == 0:
            return None, None
        beat = self.get_beat(time)
        min_error = float("inf")
        quantized_note = None
        note_enum = Rest if as_rest else Note
        for note in note_enum:
            error = note.value.beat - beat
            if abs(error) < min_error:
                min_error = error
                quantized_note = note.value
        return min_error, quantized_note

    def quantization_info(
        self, error, real_beat, quantized_note, quantization_color="color(85)"
    ):
        """info_quantization"""
        if error is not None:
            return (
                f"[{quantization_color}]"
                + f"{quantized_note.symbol:2}{quantized_note.name_kor}"
                + f"[/{quantization_color}]"
                + f"[color(249)]{float(quantized_note.beat):.3}박[/color(249)]"
                + f"[color(240)]-{float(real_beat):.3}=[/color(240)]"
                + f"[color(240)]{error}[/color(240)]"
            )
        else:
            return ""

    def note_info(self, note):
        """note_info"""
        return f"{pretty_midi.note_number_to_name(note):>3}({note})"

    def note_queue_value_address(self, value):
        """note_queue_value_address"""
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None


class MidiMessageAnalyzer_note_on(MidiMessageAnalyzer_SoundUnit):
    def print(self, blind_time=False, blind_note=False):
        note_address = self.note_queue_empty_address()
        self.note_queue[note_address] = self.msg.note

        error, quantized_note = self.quantization_min(self.msg.time, as_rest=True)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3), self.get_beat(self.msg.time), quantized_note
            )
        color = f"color({NOTE_COLOR_LIST[note_address % len(NOTE_COLOR_LIST)]})"
        note_msg = f"[{color}]┌{self.note_info(self.msg.note)}┐[/{color}]"
        if not blind_note:
            rprint(
                self.result(
                    head=note_msg,
                    body=info_quantization,
                    blind_time=blind_time,
                )
            )
        return note_address, quantization_error


class MidiMessageAnalyzer_note_off(MidiMessageAnalyzer_SoundUnit):
    def print(self, blind_time=False, blind_note=False):
        note_idx = self.note_queue_value_address(self.msg.note)
        if note_idx is None:
            color = "white on red"
        else:
            color = f"color({NOTE_COLOR_LIST[note_idx]})"
            del self.note_queue[note_idx]
        info_note_off = f"[{color}]└{self.note_info(self.msg.note)}┘[/{color}]"

        error, quantized_note = self.quantization_min(self.msg.time)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3), self.get_beat(self.msg.time), quantized_note
            )
        if not blind_note:
            rprint(
                self.result(
                    head=info_note_off,
                    body=info_quantization,
                    blind_time=blind_time,
                )
            )

        return quantization_error


class MidiMessageAnalyzer_lyrics(
    MidiMessageAnalyzer_SoundUnit, MidiMessageAnalyzer_text
):
    def __init__(
        self,
        msg,
        msg_next,
        note_address,
        ticks_per_beat,
        tempo=DEFAULT_TEMPO,
        idx=0,
        total_time=0,
        encoding="utf-8",
        encoding_alternative="cp949",
        note_queue={},
    ):
        self.msg = msg
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.total_time = total_time
        self.note_queue = note_queue
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = self.determine_encoding(encoding, encoding_alternative)
        self.msg_next = msg_next
        self.note_address = note_address

    def is_alphanum(self, str):
        for c in str:
            if c not in string.ascii_letters + string.digits:
                return False
        return True

    def print(self, border_color="#ffffff", blind_time=False, blind_note=False):
        if not self.note_queue and (
            self.msg_next.type != "note_on" or self.msg_next.time != 0
        ):  # error case
            lyric_style = "white on red"
            border_color = "white on red"
        else:
            lyric_style = "#98ff29"
            border_color = f"color({NOTE_COLOR_LIST[self.note_address]})"

        lyric = self.encoded_text.decode(self.encoding).strip()
        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = f"{lyric:^7}" if self.is_alphanum(lyric) else f"{lyric:^6}"

        error, quantized_note = self.quantization_min(self.msg.time)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3), self.get_beat(self.msg.time), quantized_note
            )
        head = border + f"[{lyric_style}]" + lyric_info + f"[/{lyric_style}]" + border
        if not blind_note:
            rprint(
                self.result(
                    head=head,
                    body=info_quantization,
                    blind_time=blind_time,
                )
            )
        return lyric, quantization_error


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
