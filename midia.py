"""midia"""

import sys
from collections import defaultdict
import string

import pretty_midi

import mido as md
from mido.midifiles.meta import MetaSpec_time_signature, add_meta_spec
from mido import MidiFile, Message, MetaMessage

from pydub import AudioSegment
from pydub.generators import Sine
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from note import (
    Note,
    Rest,
    Note_all,
    Rest_all,
    COLOR,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    DEFAULT_PPQN,
    DEFAULT_MEASURE_SPACE,
)


class MetaSpec_measure(MetaSpec_time_signature):
    """MetaSpec_measure"""

    type_byte = 0xA1
    attributes = [
        "index",
        "numerator",
        "denominator",
        "clocks_per_click",
        "notated_32nd_notes_per_beat",
    ]
    defaults = [1, 4, 4, 24, 8]


add_meta_spec(MetaSpec_measure)


def tick2beat(tick, ppqn):
    """tick2beat"""
    return tick / ppqn


def beat2tick(beat, ppqn):
    """tick2beat"""
    return int(beat * ppqn)


def midi2wav(mid_obj, wav_path, bpm):
    """Function to convert midi to wav
    ref: https://gist.github.com/jiaaro/339df443b005e12d6c2a"""

    def note_to_freq(note, concert_A=440.0):
        """
        http://en.wikipedia.org/wiki/MIDI_Tuning_Standard#Frequency_values
        """
        return (2.0 ** ((note - 69) / 12.0)) * concert_A

    output = AudioSegment.silent(mid_obj.length * 1000.0)

    def ticks_to_ms(ticks):
        tick_ms = (60000.0 / bpm) / mid_obj.ticks_per_beat
        return ticks * tick_ms

    for track in mid_obj.tracks:
        # position of rendering in ms
        current_pos = 0.0
        current_notes = defaultdict(dict)

        for msg in track:
            current_pos += ticks_to_ms(msg.time)
            if msg.type == "note_on":
                current_notes[msg.channel][msg.note] = (current_pos, msg)
            if msg.type == "note_off":
                start_pos, _ = current_notes[msg.channel].pop(msg.note)
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


def midifile2wav(midi_path, wav_path, bpm):
    """midifile2wav(midi_path, wav_path, bpm)"""
    mid = MidiFile(midi_path)
    midi2wav(mid, wav_path, bpm)


def compare_track(track1, track2):
    """compare_track"""
    i = 0
    j = 0
    while i < len(track1) or j < len(track2):
        if (
            i < len(track1)
            and track1[i].type == "note_off"
            and track1[i].note == 0
        ):
            rprint(track1[i])
            i += 1
            continue
        if (
            j < len(track2)
            and track2[j].type == "note_off"
            and track2[j].note == 0
        ):
            rprint(track1[j])
            j += 1
            continue
        if i < len(track1):
            rprint(track1[i])
            i += 1
        if j < len(track1):
            rprint(track2[j])
            j += 1
        print()


class MidiAnalyzer:
    """Class for analysis midi file"""

    def __init__(
        self,
        midi_path,
        convert_1_to_0=False,
        encoding="utf-8",
    ):
        sys.stdout.reconfigure(encoding="utf-8")  # printing encoding
        self.mid = MidiFile(midi_path)
        self.ppqn = self.mid.ticks_per_beat
        self.convert_1_to_0 = convert_1_to_0

        if self.mid.type == 1 and self.convert_1_to_0:
            self.mid.tracks = [md.merge_tracks(self.mid.tracks)]

        self.track_analyzers = [
            MidiTrackAnalyzer(
                track,
                self.ppqn,
                encoding=encoding,
                convert_1_to_0=convert_1_to_0,
            )
            for track in self.mid.tracks
        ]

    def quantization(self):
        """quantization"""
        for i, track_analyzer in enumerate(self.track_analyzers):
            self.mid.tracks[i] = track_analyzer.quantization()

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
        track_list=None,
    ):
        """method to analysis"""

        if track_bound is None:
            track_bound = float("inf")
        # meta information of midi file
        header_style = "black on white blink"
        header_info = "\n".join(
            [
                f"[{header_style}]mid file type: {self.mid.type}",
                f"ticks per beat: {self.ppqn}",
                f"total duration: {self.mid.length}[/{header_style}]",
            ]
        )
        header_panel = Panel(
            header_info,
            title="[MIDI File Header]",
            subtitle=f"{self.mid.filename}",
            style=f"{header_style}",
            border_style=f"{header_style}",
        )
        rprint(header_panel)

        quantization_error, quantization_mean = 0, 0
        for i, track_analyzer in enumerate(self.track_analyzers):
            console = Console()
            console.rule(
                "[#ffffff on #4707a8]" + f'Track {i}: "{track_analyzer.name}"'
                f"[/#ffffff on #4707a8]",
                style="#ffffff on #4707a8",
            )
            if track_list is None or track_analyzer.name in track_list:
                _quantization_error, _quantization_mean = (
                    track_analyzer.analysis(
                        track_bound=track_bound,
                        blind_note=blind_note,
                        blind_time=blind_time,
                        blind_lyric=blind_lyric,
                    )
                )
                quantization_error += _quantization_error
                quantization_mean += _quantization_mean

        if track_list is None or track_list:
            if track_list is None:
                mean_denominator = len(self.mid.tracks)
            else:
                mean_denominator = len(track_list)
            total_q_mean = quantization_mean / mean_denominator
            print()
            rprint(
                "Total quantization error/mean of track error mean: "
                + f"{float(quantization_error):.5}/"
                + f"{total_q_mean:.5}"
            )


class MidiTrackAnalyzer:
    """Class for analysis midi track"""

    def __init__(self, track, ppqn, encoding="utf-8", convert_1_to_0=False):
        self.track = track
        self.name = track.name
        self.ppqn = ppqn
        self.encoding = encoding
        self.convert_1_to_0 = convert_1_to_0
        self._init_values()

    def _init_values(self):
        self.time_signature = DEFAULT_TIME_SIGNATURE
        self.tempo = DEFAULT_TEMPO
        self.length = 0

    def _get_quantized_note(self, msg, beat):
        result = []
        if msg.type == "note_on":
            result.append(Message("note_off", time=beat2tick(beat, self.ppqn)))
        elif msg.type == "note_off":
            q_msg = msg.copy()
            q_msg.time = beat2tick(beat, self.ppqn)
            _msg_on = Message(
                "note_on", note=msg.note, velocity=msg.velocity, time=0
            )
            result.append(q_msg)
            result.append(_msg_on)
        return result

    def _quantization(self, msg):
        q_time = None
        total_q_time = 0
        error = 0
        for note_item in list(Note):
            beat = tick2beat(msg.time, self.ppqn)
            q_beat = note_item.value.beat
            q_time = beat2tick(q_beat, self.ppqn)
            if beat > q_beat:
                msg.time -= q_time
                total_q_time += q_time
            elif beat == q_beat:  # msg is quantized
                msg.time += total_q_time
                return msg, error

        # now, beat in [0, 0.125)
        beat = tick2beat(msg.time, self.ppqn)
        beat_unit = list(Note)[-1].value.beat  # 0.125
        if beat < beat_unit / 2:  # beat in [0, 0.125/2)
            error = msg.time
            msg.time = 0  # approximate to beat=0
        elif beat < beat_unit:  # beat in [0.125/2, 0.125)
            error = msg.time - beat2tick(beat_unit, self.ppqn)
            # approximate to beat=0.125
            msg.time = beat2tick(beat_unit, self.ppqn)
        msg.time += total_q_time
        return msg, error

    def quantization(self):
        """quantization2"""

        error = 0
        for msg in self.track:
            if msg.type in ["note_on", "note_off", "lyrics"]:
                if error:
                    msg.time += error
                    error = 0
                msg, error = self._quantization(msg)

        if error:
            self.track[-1].time += error
            error = 0
        return self.track

    def print_note_num(self, note_num):
        """print_note_num"""
        color = "color(240)" if note_num == 0 else "color(47)"
        bpm = round(
            md.tempo2bpm(self.tempo, time_signature=self.time_signature)
        )
        info = f"[bold {color}]Total item num of BPM({bpm}): " + f"{note_num}"
        Console(width=55).rule(info, style=f"{color}")

    def analysis(
        self,
        track_bound=None,
        blind_note=False,
        blind_time=False,
        blind_lyric=True,
    ):
        """analysis track"""
        self._init_values()
        quantization_error = 0.0
        quantization_num = 1e-6
        note_address = 0
        q_error = 0
        note_num = 0
        first_tempo = True
        note_queue = {}
        if track_bound is None:
            track_bound = float("inf")
        lyric = ""
        total_time = 0
        for i, msg in enumerate(self.track):
            if i > track_bound:
                break
            total_time += msg.time
            self.length += md.tick2second(
                msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            msg_kwarg = {
                "msg": msg,
                "ppqn": self.ppqn,
                "tempo": self.tempo,
                "idx": i,
                "length": self.length,
            }
            match msg.type:
                case "note_on":
                    result, note_address, q_error = (
                        MidiMessageAnalyzer_note_on(
                            **msg_kwarg, note_queue=note_queue
                        ).analysis(
                            blind_time=blind_time, blind_note=blind_note
                        )
                    )
                case "note_off":
                    result, q_error = MidiMessageAnalyzer_note_off(
                        **msg_kwarg, note_queue=note_queue
                    ).analysis(blind_time=blind_time, blind_note=blind_note)
                case "rest":
                    result, q_error = MidiMessageAnalyzer_rest(
                        **msg_kwarg, note_queue=note_queue
                    ).analysis(blind_time=blind_time, blind_note=blind_note)
                case "lyrics":
                    result, _lyric, q_error = MidiMessageAnalyzer_lyrics(
                        **msg_kwarg,
                        msg_next=self.track[i + 1],
                        note_address=note_address,
                        note_queue=note_queue,
                    ).analysis(blind_time=blind_time, blind_note=blind_note)
                    lyric += _lyric
                case "measure":
                    result = MidiMessageAnalyzer_measure(
                        self.time_signature
                    ).analysis()
                case "text" | "track_name":
                    result = MidiMessageAnalyzer_text(
                        **msg_kwarg,
                        encoding=self.encoding,
                    ).analysis(blind_time=blind_time)
                case "set_tempo":
                    if not first_tempo and self.convert_1_to_0:
                        self.print_note_num(note_num)
                    first_tempo = False
                    result, self.tempo = MidiMessageAnalyzer_set_tempo(
                        **msg_kwarg,
                        time_signature=self.time_signature,
                    ).analysis(blind_time=blind_time)
                case "end_of_track":
                    if self.convert_1_to_0:
                        self.print_note_num(note_num)
                    result = MidiMessageAnalyzer_end_of_track(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "key_signature":
                    result = MidiMessageAnalyzer_key_signature(
                        **msg_kwarg
                    ).analysis(blind_time=blind_time)
                case "time_signature":
                    result, self.time_signature = (
                        MidiMessageAnalyzer_time_signature(
                            **msg_kwarg
                        ).analysis(blind_time=blind_time)
                    )
                case _:
                    result = MidiMessageAnalyzer(**msg_kwarg).analysis(
                        blind_time=blind_time
                    )

            if result:
                rprint(result)

            if msg.type in ["note_on", "note_off", "lyrics"]:
                quantization_error += q_error
                quantization_num += 1 if q_error else 0
                note_num += 1

        rprint(f"Track lyric encode: {self.encoding}")
        rprint(f"Track total time: {self.length}/{total_time}")
        q_error_mean = quantization_error / quantization_num
        rprint(
            "Track total quantization error/mean: "
            + f"{quantization_error:.5}/"
            + f"{q_error_mean: .5}"
        )
        if not blind_lyric:
            print(f'LYRIC: "{lyric}"')
        return quantization_error, q_error_mean


class MidiMessageAnalyzer:
    """MidiMessageAnalyzer"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length

    def info_type(self):
        """info_type"""
        return f"[black on white]\\[{self.msg.type}][/black on white]"

    def info_time(self):
        """time_info"""
        if self.msg.time:
            main_color = "#ffffff"
            sub_color = "white"
            time = md.tick2second(
                self.msg.time,
                ticks_per_beat=self.ppqn,
                tempo=self.tempo,
            )
            return " ".join(
                [
                    f"[{main_color}]{time:4.2f}[/{main_color}]"
                    + f"[{sub_color}]/{self.length:6.2f}[/{sub_color}]",
                    f"[{sub_color}]time=[/{sub_color}]"
                    + f"[{main_color}]{self.msg.time:<3}[/{main_color}]",
                ]
            )
        else:
            return ""

    def result(self, head="", body="", blind_time=False):
        """print strings"""
        time_info = "" if blind_time else self.info_time()
        _result = [self.idx_info, head, time_info, body]
        return " ".join([s for s in _result if s])

    def analysis(self, blind_time=False):
        """analysis"""
        return self.result(
            head=self.info_type(),
            body=f"[color(250)]{self.msg}[/color(250)]",
            blind_time=blind_time,
        )


class MidiMessageAnalyzer_set_tempo(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_set_tempo"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self.time_signature = time_signature

    def analysis(self, blind_time=False):
        bpm = round(
            md.tempo2bpm(self.msg.tempo, time_signature=self.time_signature)
        )
        result = self.result(
            head=self.info_type(),
            body=f"[white]BPM=[/white][color(190)]{bpm}[/color(190)]",
            blind_time=blind_time,
        )
        return result, self.msg.tempo


class MidiMessageAnalyzer_key_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_key_signature"""

    def analysis(self, blind_time=False):
        return self.result(
            head=self.info_type(), body=self.msg.key, blind_time=blind_time
        )


class MidiMessageAnalyzer_end_of_track(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_end_of_track"""

    def analysis(self, blind_time=False):
        return self.result(head=self.info_type(), blind_time=blind_time)


class MidiMessageAnalyzer_time_signature(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_time_signature"""

    def analysis(self, blind_time=False):
        result = self.result(
            head=self.info_type(),
            body=f"{self.msg.numerator}/{self.msg.denominator}",
            blind_time=blind_time,
        )
        return result, (self.msg.numerator, self.msg.denominator)


class MidiMessageAnalyzer_measure(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_measure"""

    idx = 1

    def __init__(
        self,
        time_signature=DEFAULT_TIME_SIGNATURE,
    ):
        self.time_signature = time_signature

    @classmethod
    def inc_idx(cls):
        """inc_idx"""
        cls.idx += 1

    def analysis(self):
        """print measure"""
        Console(width=50).rule(
            f"[#ffffff]𝄞 {self.time_signature[0]}/{self.time_signature[1]} "
            + f"measure {self.idx}[/#ffffff]",
            style="#ffffff",
            characters="=",
        )
        self.inc_idx()
        return ""


class MidiMessageAnalyzer_text(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_text"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
    ):
        super().__init__(msg, ppqn, tempo=tempo, idx=idx, length=length)
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )

    def _init_encoding(self, encoding="utf-8", encoding_alternative="cp949"):
        self.encoded_text = self.msg.bin()[3:]
        self.encoding = self.determine_encoding(encoding, encoding_alternative)

    def determine_encoding(self, *encoding_list):
        """determine_encoding"""
        for encoding in encoding_list:
            try:
                self.encoded_text.decode(encoding)
            except UnicodeDecodeError:
                continue
            else:
                return encoding
        raise UnicodeDecodeError

    def analysis(self, blind_time=False):
        """analysis text"""
        text = self.encoded_text.decode(self.encoding).strip()
        return self.result(
            head=self.info_type(), body=text, blind_time=blind_time
        )


class MidiMessageAnalyzer_SoundUnit(MidiMessageAnalyzer):
    """MidiMessageAnalyzer_SoundUnit"""

    def __init__(
        self,
        msg,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        note_queue=None,
    ):
        super().__init__(
            msg,
            ppqn,
            tempo=tempo,
            idx=idx,
            length=length,
        )
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue

    def note_queue_find(self, value):
        """note_queue_find"""
        for k, v in self.note_queue.items():
            if v == value:
                return k
        return None

    def note_queue_alloc(self):
        """note_queue_alloc"""
        address = 0
        while True:
            try:
                self.note_queue[address]
                address += 1
            except KeyError:
                return address

    def closest_note(self, tick, as_rest=False):
        """select minimum error"""
        if tick == 0:
            return None, None
        beat = tick2beat(tick, self.ppqn)
        min_error = float("inf")
        quantized_note = None
        note_enum = Rest_all if as_rest else Note_all
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
        if error is None:
            return ""
        else:
            if error == 0:
                err_msg = ""
            else:
                err_msg = (
                    f"[red]-{float(real_beat):.3}[/red]"
                    + f"[#ff0000]={error}[/#ff0000]"
                )
            return (
                f"[{quantization_color}]"
                + f"{quantized_note.symbol:2}{quantized_note.name_short}"
                + f"[/{quantization_color}] "
                + f"[color(249)]{float(quantized_note.beat):.3}b[/color(249)]"
                + err_msg
            )

    def note_info(self, note):
        """note_info"""
        return f"{pretty_midi.note_number_to_name(note):>3}({note})"


class MidiMessageAnalyzer_note_on(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_on"""

    def alloc_note(self, note):
        """alloc_note"""
        note_address = self.note_queue_alloc()
        self.note_queue[note_address] = note
        return note_address

    def analysis(self, blind_time=False, blind_note=False):
        addr = self.alloc_note(self.msg.note)
        error, quantized_note = self.closest_note(self.msg.time, as_rest=True)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        color = f"color({COLOR[addr % len(COLOR)]})"
        note_msg = f"[{color}]┌{self.note_info(self.msg.note)}┐[/{color}]"
        result = ""
        if not blind_note:
            result = self.result(
                head=note_msg, body=info_quantization, blind_time=blind_time
            )
        return result, addr, quantization_error


class MidiMessageAnalyzer_note_off(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_note_off"""

    def free_note(self, note):
        """alloc_note"""
        addr = self.note_queue_find(note)
        if addr is not None:
            del self.note_queue[addr]
        return addr

    def analysis(self, blind_time=False, blind_note=False):
        addr = self.free_note(self.msg.note)
        color = None if addr is None else f"color({COLOR[addr % len(COLOR)]})"

        error, quantized_note = self.closest_note(
            self.msg.time, as_rest=True if addr is None else False
        )
        if color:
            _note_info = self.note_info(self.msg.note)
            info_note_off = f"[{color}]└{_note_info}┘[/{color}]"
        else:
            info_note_off = f"[#ffffff]{quantized_note.symbol:^9}[/#ffffff]"
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        if not blind_note:
            result = self.result(
                head=info_note_off,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result, quantization_error


class MidiMessageAnalyzer_rest(MidiMessageAnalyzer_SoundUnit):
    """MidiMessageAnalyzer_rest"""

    def analysis(self, blind_time=False, blind_note=False):
        error, quantized_note = self.closest_note(self.msg.time, as_rest=True)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        result = ""
        info_rest = f"[black on white]{quantized_note.symbol}[/black on white]"
        info_rest = f"{info_rest:^19}"
        info_rest = f"[#ffffff]{quantized_note.symbol:^9}[/#ffffff]"
        if not blind_note:
            result = self.result(
                head=info_rest,
                body=info_quantization,
                blind_time=blind_time,
            )

        return result, quantization_error


class MidiMessageAnalyzer_lyrics(
    MidiMessageAnalyzer_SoundUnit, MidiMessageAnalyzer_text
):
    """MidiMessageAnalyzer_lyrics"""

    def __init__(
        self,
        msg,
        msg_next,
        note_address,
        ppqn=DEFAULT_PPQN,
        tempo=DEFAULT_TEMPO,
        idx=0,
        length=0,
        encoding="utf-8",
        encoding_alternative="cp949",
        note_queue=None,
    ):
        self.msg = msg
        self.ppqn = ppqn
        self.tempo = tempo
        self.idx_info = f"[color(244)]{idx:4}[/color(244)]"
        self.length = length
        if note_queue is None:
            self.note_queue = {}
        else:
            self.note_queue = note_queue
        self._init_encoding(
            encoding=encoding, encoding_alternative=encoding_alternative
        )
        self.msg_next = msg_next
        self.note_address = note_address

    def is_alnumpunc(self, s):
        """is_alnumpunc"""
        candidate = string.ascii_letters + string.digits + string.punctuation
        for c in s:
            if c not in candidate:
                return False
        return True

    def analysis(
        self, blind_time=False, border_color="#ffffff", blind_note=False
    ):
        if not self.note_queue and (
            self.msg_next.type != "note_on" or self.msg_next.time != 0
        ):  # error case
            lyric_style = "white on red"
            border_color = "white on red"
        else:
            lyric_style = "#98ff29"
            border_color = f"color({COLOR[self.note_address % len(COLOR)]})"

        lyric = self.encoded_text.decode(self.encoding).strip()
        border = f"[{border_color}]│[/{border_color}]"
        lyric_info = (
            f"{lyric:^7}" if self.is_alnumpunc(lyric) else f"{lyric:^6}"
        )

        error, quantized_note = self.closest_note(self.msg.time)
        info_quantization = ""
        quantization_error = 0
        if error is not None:
            quantization_error = abs(error)
            info_quantization = self.quantization_info(
                round(error, 3),
                tick2beat(self.msg.time, self.ppqn),
                quantized_note,
            )
        head = (
            border
            + f"[{lyric_style}]"
            + lyric_info
            + f"[/{lyric_style}]"
            + border
        )
        result = ""
        if not blind_note:
            result = self.result(
                head=head,
                body=info_quantization,
                blind_time=blind_time,
            )
        return result, lyric, quantization_error
